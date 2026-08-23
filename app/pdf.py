import io
import logging

import pdfplumber
import pymupdf

logger = logging.getLogger(__name__)

def extract_text(pdf: bytes) -> str:
    """Извлекает текст через pdfplumber"""
    logger.debug("[pdf.py] call extract_text()")

    try:
        return extract_text_with_pdfplumber(pdf)
    except Exception:
        logger.debug("pdfplumber: не удалось извлечь текст")
        return ""


def extract_text_with_pdfplumber(pdf: bytes) -> str:
    """Постраничное извлечение текста через pdfplumber"""
    logger.debug("[pdf.py] call extract_text_with_pdfplumber()")

    pages: list[str] = []
    with pdfplumber.open(io.BytesIO(pdf)) as doc:
        logger.debug("pdfplumber: pages=%d", len(doc.pages))
        for page in doc.pages:
            text = page.extract_text() or ""
            pages.append(text)
    result = "\n\n".join(t for t in pages if t.strip())
    logger.debug("pdfplumber: chars=%d", len(result))
    return result


def render_pages(pdf: bytes, max_pages: int, dpi: int = 200) -> list[bytes]:
    """Рендерит страницы PDF в PNG-байты"""
    logger.debug("[pdf.py] call render_pages()")

    pages: list[bytes] = []
    scale = dpi / 72
    with pymupdf.open(stream=pdf, filetype="pdf") as doc:
        for index, page in enumerate(doc):
            if index >= max_pages:
                break
            pixmap = page.get_pixmap(matrix=pymupdf.Matrix(scale, scale))
            pages.append(pixmap.tobytes("png"))
    logger.debug("render_pages: отрендерено %d страниц (max_pages=%d)", len(pages), max_pages)
    return pages
