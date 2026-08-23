from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # LLM
    llm_api_key: str = Field(default="")
    llm_base_url: str = Field(default="https://api.openai.com/v1")
    llm_model: str = Field(default="gpt-4o-mini")
    llm_temperature: float = Field(default=0.0)
    llm_max_tokens: int = Field(default=2000)
    llm_timeout: float = Field(default=120.0)

    max_pages: int = Field(default=50, description="Макс. страниц для рендера")
    prompt_file: str = Field(default="app/prompts/extract.md")
    log_level: str = Field(default="INFO")
    analysis_mode: Literal["local", "cloud"] = Field(default="local")

@lru_cache
def get_settings() -> Settings:
    return Settings()
