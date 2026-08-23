from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # LLM
    llm_api_key: str = Field(default="")
    llm_base_url: str = Field(default="https://api.openai.com/v1")
    llm_model: str = Field(default="gpt-4o-mini")
    llm_temperature: float = Field(default=0.0)
    llm_max_tokens: int = Field(default=2000)
    llm_timeout: float = Field(default=120.0)


@lru_cache
def get_settings() -> Settings:
    return Settings()
