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

    # Гибридная схема извлечения текста
    pdf_min_chars: int = Field(default=300, description="Мин. символов текста")
    ocr_enabled: bool = Field(default=True)
    ocr_lang: str = Field(default="rus")
    max_pages: int = Field(default=50, description="Макс. страниц для OCR/рендера")
    media_max_images: int = Field(default=5, description="Страниц-картинок в vision-модель")
    prompt_file: str = Field(default="app/prompts/extract.md")
    log_level: str = Field(default="INFO")
    analysis_mode: Literal["local", "cloud"] = Field(default="local")

@lru_cache
def get_settings() -> Settings:
    return Settings()
