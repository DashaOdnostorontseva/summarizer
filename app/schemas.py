from typing import Literal

from pydantic import BaseModel, Field


class ContractAmount(BaseModel):
    """Сумма контракта (цена)."""

    amount: float | None = Field(default=None, description="Числовое значение суммы")
    currency: str | None = Field(default=None, description="Валюта, например RUB")
    raw: str | None = Field(default=None, description="Сумма как записана в документе")


class Fine(BaseModel):
    """Штраф / пеня / неустойка."""

    description: str | None = Field(default=None, description="Содержание штрафа")
    amount: str | None = Field(default=None, description="Сумма/ставка как в документе")
    basis: str | None = Field(default=None, description="Основание: пункт, статья, раздел")


class ExtractionResult(BaseModel):
    """Результат анализа тендерной документации."""

    contract_amount: ContractAmount | None = Field(default=None, description="Сумма контракта")
    deadline: str | None = Field(default=None, description="Сроки выполнения/поставки")
    contractor_requirements: list[str] = Field(
        default_factory=list, description="Ключевые требования к исполнителю"
    )
    fines: list[Fine] = Field(default_factory=list, description="Список штрафов")
    status: Literal["extracted", "partial"] = Field(default="extracted")
    notes: str | None = Field(default=None, description="Комментарии модели")
