from __future__ import annotations

import logging

from fastapi import FastAPI, File, Form, HTTPException, UploadFile

from . import extract
from .config import get_settings
from .llm import LLMClient, LLMError
from .logging_conf import setup_logging
from .schemas import ExtractionResult, ProcessMode

logger = logging.getLogger(__name__)

settings = get_settings()
setup_logging(settings.log_level)

app = FastAPI(title="PDF Summarizer", version="0.1.0")

_client: LLMClient | None = None


def get_client() -> LLMClient:
    global _client
    if _client is None:
        _client = LLMClient(settings)
    return _client

_ALLOWED_MIME = {None, "application/pdf", "application/octet-stream"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/analyze", response_model=ExtractionResult)
def analyze(
    file: UploadFile = File(...),
    mode: ProcessMode = Form(default=settings.analysis_mode),
) -> ExtractionResult:
    if file.content_type not in _ALLOWED_MIME:
        raise HTTPException(status_code=400, detail="Ожидается PDF-файл (application/pdf)")

    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Файл должен иметь расширение .pdf")

    data = file.file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Пустой файл")
    
    logger.debug("Файл получен: %s (%d байт)", filename, len(data))

    try:
        doc = extract.extract_document(data, settings, mode=mode)
    except Exception as exc:
        logger.exception("Ошибка извлечения из PDF")
        raise HTTPException(status_code=422, detail="Не удалось прочитать PDF-файл") from exc

    logger.debug("Извлечение: source=%s mode=%s", doc.source, mode)

    if doc.source == extract.SOURCE_NONE:
        if mode == extract.MODE_LOCAL:
            raise HTTPException(
                status_code=422,
                detail="Не удалось прочитать текст из документа (вероятно, это скан). "
                "Попробуйте mode=cloud.",
            )
        raise HTTPException(status_code=422, detail="Не удалось отрендерить страницы PDF")

    if not settings.llm_api_key:
        raise HTTPException(status_code=500, detail="LLM_API_KEY не задан")

    try:
        return get_client().extract(doc)
    except LLMError as exc:
        logger.error("Ошибка LLM: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc