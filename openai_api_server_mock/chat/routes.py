from typing import List

import asyncio
from fastapi import APIRouter, HTTPException

from .models import CompletionRequest, Usage, CompletionResponse, Choice
from .surrogates import get_surrogate
from ..utils import get_logger
from ..settings import settings


router = APIRouter(prefix="/chat")
logger = get_logger()

logger.debug(f"Setting up semaphore with {settings.max_concurrent_requests} permits")
semaphore = asyncio.Semaphore(settings.max_concurrent_requests)
concurrency_lock = asyncio.Lock()
concurrency_counter = 0


@router.post("/completions", tags=["chat"])
async def create_chat_completion(request: CompletionRequest) -> CompletionResponse:
    logger.debug(f"Received completion request with {len(request.messages)} message(s)")

    global semaphore
    global concurrency_lock
    global concurrency_counter

    async with concurrency_lock:
        concurrency_counter += 1
        if concurrency_counter > settings.max_concurrent_requests:
            logger.warning("Too many concurrent requests")

    async with semaphore:
        if settings.sleep_time:
            logger.debug(f"Sleeping for {settings.sleep_time} seconds")
            await asyncio.sleep(settings.sleep_time)

        logger.debug(f"Generating {request.n} completion(s)")
        try:
            surrogate = await get_surrogate(request.model)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        choices: List[Choice] = []
        for i in range(request.n):
            choice = await surrogate.generate_completion(
                i,
                request.messages,
                max_tokens=request.max_tokens,
                logprobs=request.logprobs,
                top_logprobs=request.top_logprobs,
            )
            choices.append(choice)

        logger.debug("Evaluating usage")
        n_prompt_tokens = sum(
            len(string.split(" "))
            for string in [message.content for message in request.messages]
        )
        n_completion_tokens = sum(
            len(choice.message.content.split(" ")) for choice in choices
        )

        async with concurrency_lock:
            concurrency_counter -= 1

    return CompletionResponse(
        id="mock_123",
        choices=choices,
        model=request.model,
        service_tier=request.service_tier,
        system_fingerprint="mock",
        usage=Usage(
            prompt_tokens=n_prompt_tokens,
            completion_tokens=n_completion_tokens,
            total_tokens=n_prompt_tokens + n_completion_tokens
        ),
    )
