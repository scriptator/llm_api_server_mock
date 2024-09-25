from typing import List, Optional
from abc import ABC, abstractmethod
from lorem_text import lorem
import random
from math import log, exp

from .models import Message, LogProb, LogProbs, Choice, LogProbInner
from ..settings import settings


available_surrogates = []


class ModelSurrogate(ABC):
    name: str

    @classmethod
    @abstractmethod
    async def generate(cls, n: int, messages: List[Message]) -> List[str]:
        pass

    @classmethod
    async def generate_completion(
        cls,
        index: int,
        messages: List[Message],
        max_tokens: Optional[int] = None,
        logprobs: Optional[bool] = False,
        top_logprobs: Optional[int] = None,
    ):
        tokens = await cls.generate(random.randint(10, settings.context_size), messages)

        if max_tokens is None or (max_tokens > len(tokens)):
            finish_reason = "stop"
        else:
            tokens = tokens[:max_tokens]
            finish_reason = "length"

        if logprobs:
            logprobs_list: List[LogProb] = [
                LogProb(
                    token=token,
                    logprob=log(random.uniform(0.01, 1.0)),
                    bytes=None,
                    top_logprobs=None
                )
                for token in tokens
            ]
            if top_logprobs:
                for log_prob in logprobs_list:
                    log_prob.top_logprobs = []
                    for _ in range(top_logprobs):
                        tokens = await cls.generate(1, messages)
                        log_prob.top_logprobs.append(
                            LogProbInner(
                                token=tokens[0],
                                logprob=log(random.uniform(0.01, exp(log_prob.logprob))),
                                bytes=None,
                            )
                        )

        choice = Choice(
            finish_reason=finish_reason,
            index=index,
            message=Message(role="assistant", content=" ".join(tokens)),
            logprobs=LogProbs(content=logprobs_list) if logprobs else None,
        )
        return choice

    @classmethod
    def register(cls):
        global available_surrogates
        available_surrogates.append(cls)


class LoremIpsumSurrogate(ModelSurrogate):
    name: str = "lorem_ipsum"

    @classmethod
    async def generate(cls, n: int, messages: List[Message]) -> List[str]:
        return lorem.words(n).split(" ")


LoremIpsumSurrogate.register()


class YesNoSurrogate(ModelSurrogate):
    name: str = "yes_no"

    @classmethod
    async def generate(cls, n: int, messages: List[Message]) -> List[str]:
        return ["Yes" if random.random() > 0.5 else "No"]


YesNoSurrogate.register()


class JaNeinSurrogate(ModelSurrogate):
    name: str = "ja_nein"

    @classmethod
    async def generate(cls, n: int, messages: List[Message]) -> List[str]:
        return ["Ja" if random.random() > 0.5 else "Nein"]


JaNeinSurrogate.register()


async def get_surrogate(model: str) -> ModelSurrogate:
    global available_surrogates
    for surrogate in available_surrogates:
        if surrogate.name == model:
            return surrogate
    raise ValueError(f"Surrogate {model} not found.")
