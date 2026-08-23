import logging
from dataclasses import dataclass

from . import ocr, pdf
from .config import Settings

# Источники содержимого, которое уходит в LLM.
SOURCE_PDFPLUMBER = "pdfplumber"
SOURCE_OCR = "ocr"
SOURCE_MEDIA = "media"
SOURCE_NONE = "none"

# Способы обработки запроса.
MODE_LOCAL = "local"
MODE_CLOUD = "cloud"

logger = logging.getLogger(__name__)


@dataclass
class ExtractedDoc:
    """Результат извлечения."""

    content: str
    source: str
    page_images: list[bytes]


def extract_document(
    pdf_bytes: bytes, settings: Settings, mode: str = MODE_LOCAL
) -> ExtractedDoc:
    """Ищет содержимое в зависимости от режима.

    local — локальное извлечение текста (pdfplumber или tesseract OCR), текст уходит в LLM;
    cloud — страницы-картинки отправляются напрямую в мультимодальную модель.
    """
    logger.debug("extract_document: mode=%s pdf_bytes=%d", mode, len(pdf_bytes))

    if mode == MODE_CLOUD:
        return _extract_media(pdf_bytes, settings)

    return _extract_local(pdf_bytes, settings)


def _extract_local(pdf_bytes: bytes, settings: Settings) -> ExtractedDoc:
    """pdfplumber или tesseract OCR"""
    text = pdf.extract_text(pdf_bytes)
    text_len = len(text.strip())
    logger.debug("local: pdfplumber chars=%d (min=%d)", text_len, settings.pdf_min_chars)
    if text_len >= settings.pdf_min_chars:
        logger.debug("local: источник pdfplumber, текст полный")
        return ExtractedDoc(content=text, source=SOURCE_PDFPLUMBER, page_images=[])

    if settings.ocr_enabled:
        page_images = pdf.render_pages(pdf_bytes, max_pages=settings.max_pages)
        ocr_text = ocr.ocr_pages(page_images, lang=settings.ocr_lang)
        ocr_len = len(ocr_text.strip())
        logger.debug(
            "local: ocr chars=%d (min=%d) pages=%d",
            ocr_len, settings.pdf_min_chars, len(page_images),
        )
        if ocr_len >= settings.pdf_min_chars:
            logger.debug("local: источник ocr, текст полный")
            return ExtractedDoc(content=ocr_text, source=SOURCE_OCR, page_images=[])

    logger.debug("local: источник не найден (source=none)")
    return ExtractedDoc(content="", source=SOURCE_NONE, page_images=[])


def _extract_media(pdf_bytes: bytes, settings: Settings) -> ExtractedDoc:
    """Рендерит страницы и отдает их как медиа в vision-модель."""
    page_images = pdf.render_pages(pdf_bytes, max_pages=settings.max_pages)
    logger.debug(
        "cloud: отрендерено страниц=%d (max_pages=%d)", len(page_images), settings.max_pages
    )
    if not page_images:
        logger.debug("cloud: страницы не отрендерены (source=none)")
        return ExtractedDoc(content="", source=SOURCE_NONE, page_images=[])
    logger.debug("cloud: источник media, страниц=%d", len(page_images))
    return ExtractedDoc(content="", source=SOURCE_MEDIA, page_images=page_images)
