import logging
from dataclasses import dataclass

from . import pdf

logger = logging.getLogger(__name__)


@dataclass
class ExtractedDoc:
    """Результат извлечения."""

    content: str


def extract_document(pdf_bytes: bytes) -> ExtractedDoc:
    logger.debug("extract_document: pdf_bytes=%d", len(pdf_bytes))

    return _extract_local(pdf_bytes)


def _extract_local(pdf_bytes: bytes) -> ExtractedDoc:
    text = pdf.extract_text(pdf_bytes)
    text_len = len(text.strip())
    logger.debug("local: pdfplumber chars=%d", text_len)
    return ExtractedDoc(content=text)