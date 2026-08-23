from __future__ import annotations

from fastapi import FastAPI, File, HTTPException, UploadFile

from . import extract
from .schemas import ExtractionResult

app = FastAPI(title="PDF Summarizer", version="0.1.0")


_ALLOWED_MIME = {None, "application/pdf", "application/octet-stream"}


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/analyze", response_model=ExtractionResult)
def analyze(file: UploadFile = File(...)) -> ExtractionResult:
    if file.content_type not in _ALLOWED_MIME:
        raise HTTPException(status_code=400, detail="Ожидается PDF-файл (application/pdf)")

    filename = file.filename or ""
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Файл должен иметь расширение .pdf")

    data = file.file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Пустой файл")

    try:
        result = extract.extract_document(data)
        return result
    except Exception as exc:
        raise HTTPException(status_code=422, detail="Не удалось прочитать PDF-файл") from exc