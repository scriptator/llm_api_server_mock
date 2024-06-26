from typing import List, Optional, Mapping, Union
from datetime import datetime
from pydantic import BaseModel, Field

from ..settings import settings


class Message(BaseModel):
    role: str = Field(...)
    content: str = Field(...)
    name: Optional[str] = Field(default=None)


class CompletionRequest(BaseModel):
    messages: List[Message] = Field(..., min_items=1)
    model: str = Field(...)
    frequency_penalty: Optional[float] = Field(default=None, ge=-2.0, le=2.0)
    logit_bias: Optional[Mapping[str, float]] = Field(default=None)
    logprobs: Optional[bool] = Field(default=False)
    top_logprobs: Optional[int] = Field(None, ge=1, le=20)
    max_tokens: Optional[int] = Field(None, ge=1, le=settings.context_size)
    n: Optional[int] = Field(1, ge=1)
    presence_penalty: Optional[float] = Field(0.0, ge=-2.0, le=2.0)
    response_format: Optional[dict] = Field(default=None)
    seed: Optional[int] = Field(None, ge=0)
    service_tier: Optional[str] = Field(default=None)
    stop: Optional[Union[str, List]] = Field(default=None)
    stream: Optional[bool] = Field(default=None)
    stream_options: Optional[dict] = Field(default=None)
    temperature: Optional[float] = Field(1.0, ge=0.0, le=2.0)
    top_p: Optional[float] = Field(1.0, ge=0.0, le=1.0)
    tools: Optional[List[str]] = Field(default=None)


class LogProbInner(BaseModel):
    token: str = Field(...)
    logprob: float = Field(...)
    logprob_bytes: Optional[bytes] = Field(None, alias="bytes")


class LogProb(LogProbInner):
    top_logprobs: Optional[List[LogProbInner]] = Field(default=None)


class LogProbs(BaseModel):
    content: List[LogProb] = Field(...)


class Choice(BaseModel):
    finish_reason: str = Field(...)
    index: int = Field(...)
    message: Message = Field(...)
    logprobs: Optional[LogProbs] = Field(default=None)


class Usage(BaseModel):
    prompt_tokens: int = Field(...)
    completion_tokens: int = Field(...)
    total_tokens: int = Field(...)


class CompletionResponse(BaseModel):
    id: str = Field(...)
    choices: List[Choice] = Field(...)
    created: float = Field(default_factory=datetime.now().timestamp)
    model: str = Field(...)
    service_tier: Optional[str] = Field(default=None)
    system_fingerprint: str = Field(...)
    object: str = Field(default="chat.completion")
    usage: Usage = Field(...)
