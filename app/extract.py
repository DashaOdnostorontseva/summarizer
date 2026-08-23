import logging
from dataclasses import dataclass

from . import pdf
from .config import Settings

# Способы обработки запроса.
MODE_LOCAL = "local"
MODE_CLOUD = "cloud"

logger = logging.getLogger(__name__)


@dataclass
class ExtractedDoc:
    """Результат извлечения."""

    content: str
    page_images: list[bytes]


def extract_document(
    pdf_bytes: bytes, settings: Settings, mode: str = MODE_LOCAL
) -> ExtractedDoc:
    """Ищет содержимое в зависимости от режима.

    local — локальное извлечение текста, текст уходит в LLM;
    cloud — страницы-картинки отправляются напрямую в мультимодальную модель.
    """
    logger.debug("extract_document: mode=%s pdf_bytes=%d", mode, len(pdf_bytes))

    if mode == MODE_CLOUD:
        return _extract_media(pdf_bytes, settings)

    return _extract_local(pdf_bytes, settings)


def _extract_local(pdf_bytes: bytes, settings: Settings) -> ExtractedDoc:
    text = pdf.extract_text(pdf_bytes)
    text_len = len(text.strip())
    return ExtractedDoc(content=text, page_images=[])
def _extract_media(pdf_bytes: bytes, settings: Settings) -> ExtractedDoc:
    """Рендерит страницы и отдает их как медиа в vision-модель."""
    page_images = pdf.render_pages(pdf_bytes, max_pages=settings.max_pages)
    logger.debug(
        "cloud: отрендерено страниц=%d (max_pages=%d)", len(page_images), settings.max_pages
    )
    if not page_images:
        logger.debug("cloud: страницы не отрендерены (source=none)")
        return ExtractedDoc(content="", page_images=[])
    logger.debug("cloud: источник media, страниц=%d", len(page_images))
    return ExtractedDoc(content="", page_images=page_images)
