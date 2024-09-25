from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    context_size: int = Field(alias="CONTEXT_SIZE", default=4096)
    sleep_time: int = Field(alias="SLEEP_TIME", default=0)
    max_concurrent_requests: int = Field(
        alias="MAX_CONCURRENT_REQUESTS", default=10**9
    )
    language: Literal["en", "de"] = Field(alias="LANGUAGE", default="en")


settings = Settings()
