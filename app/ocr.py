import io
import logging

import pytesseract
from PIL import Image

logger = logging.getLogger(__name__)


def ocr_pages(page_images: list[bytes], lang: str) -> str:
    """Распознает текст на отрендеренных страницах и склеивает его"""
    logger.debug("ocr: images=%d lang=%s", len(page_images), lang)
    texts: list[str] = []
    for image_bytes in page_images:
        try:
            with Image.open(io.BytesIO(image_bytes)) as image:
                text = pytesseract.image_to_string(image, lang=lang)
        except pytesseract.TesseractNotFoundError:
            logger.warning("Двоичный файл tesseract не найден. OCR недоступен.")
            return ""
        except Exception as exc:
            logger.warning("Ошибка OCR (%s): %s", type(exc).__name__, exc)
            return ""
        if text.strip():
            texts.append(text.strip())
    result = "\n\n".join(texts)
    logger.debug("ocr: распознано %d символов", len(result))
    return result
