import json
import logging

from openai import OpenAI

from .config import Settings
from .extract import ExtractedDoc
from .schemas import ExtractionResult

logger = logging.getLogger(__name__)

MAX_TEXT_CHARS = 120_000


class LLMError(Exception):
    """Ошибка на стороне LLM"""


class LLMClient:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.client = OpenAI(
            api_key=settings.llm_api_key,
            base_url=settings.llm_base_url,
            timeout=settings.llm_timeout,
        )
        self.prompt_template = self._load_prompt()

    @staticmethod
    def _load_prompt() -> str:
        return "Извлеки из документа структурированные данные и верни строгий JSON."
    
    def _build_system_message(self) -> str:
        logger.debug("[llm.py] call _build_system_message()")

        schema = json.dumps(
            ExtractionResult.model_json_schema(), ensure_ascii=False, indent=2
        )
        return (
            f"{self.prompt_template}\n\n"
            "Верни строгий JSON, соответствующий такой схеме (без пояснений и markdown):\n"
            f"{schema}"
        )

    def _user_content(self, doc: ExtractedDoc):
        logger.debug("[llm.py] call _user_content()")

        content = doc.content
        if len(content) > MAX_TEXT_CHARS:
            logger.debug(
                "text: длина %d, отправлено %d (MAX_TEXT_CHARS=%d) — ОБРЕЗАНО",
                len(content), MAX_TEXT_CHARS, MAX_TEXT_CHARS,
            )
            content = content[:MAX_TEXT_CHARS]
        else:
            logger.debug("text: длина %d — ПОЛНОСТЬЮ", len(content))
        return content

    @staticmethod
    def _parse_json(content: str) -> dict:
        logger.debug("[llm.py] call _parse_json()")

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end > start:
            try:
                return json.loads(content[start : end + 1])
            except json.JSONDecodeError:
                pass
        raise LLMError("Ответ модели не удалось разобрать как JSON")

    def _call(self, messages: list[dict]) -> dict:
        logger.debug("[llm.py] call _call()")

        base = dict(
            model=self.settings.llm_model,
            messages=messages,
            temperature=self.settings.llm_temperature,
            max_tokens=self.settings.llm_max_tokens,
        )
        attempts: list[dict] = []
        attempts.append({**base, "response_format": {"type": "json_object"}})

        last_error: str | Exception | None = None
        for index, kwargs in enumerate(attempts, start=1):
            label = "json" if kwargs.get("response_format") else "plain"
            logger.debug(
                "call: попытка %d/%d (%s) model=%s",
                index, len(attempts), label, self.settings.llm_model,
            )
            try:
                response = self.client.chat.completions.create(**kwargs)
                content = response.choices[0].message.content or ""
                return self._parse_json(content)
            except LLMError as exc:
                last_error = exc
                logger.warning("Ответ LLM не удалось разобрать как JSON: %s", exc)
            except Exception as exc:
                last_error = exc
                logger.warning("Попытка вызова LLM не удалась: %s", exc)

        raise LLMError(f"Ошибка вызова LLM: {last_error}")

    def extract(self, doc: ExtractedDoc) -> ExtractionResult:
        logger.debug(
            "extract: content_len=%d",
            len(doc.content),
        )

        if not self.settings.llm_api_key:
            raise LLMError("LLM_API_KEY не задан")

        user_content = self._user_content(doc)
        messages = [
            {"role": "system", "content": self._build_system_message()},
            {"role": "user", "content": user_content},
        ]
        data = self._call(messages)
        return ExtractionResult.model_validate(data)
