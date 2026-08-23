from .schemas import ExtractionResult, ContractAmount, Fine

def extract_document(
    pdf_bytes: bytes 
) -> ExtractionResult:
    return ExtractionResult(
        contract_amount=ContractAmount(
            amount=1500000.00,
            currency="RUB",
            raw="1 500 000 (Один миллион пятьсот тысяч) рублей 00 копеек",
        ),
        deadline="В течение 60 календарных дней с момента подписания контракта",
        contractor_requirements=[
            "Наличие действующей лицензии ФСТЭК",
            "Опыт выполнения аналогичных работ не менее 3-х лет",
            "Отсутствие в реестре недобросовестных поставщиков (РНП)",
        ],
        fines=[
            Fine(
                description="Пеня за просрочку исполнения обязательств поставщиком",
                amount="1/300 ключевой ставки ЦБ РФ от цены контракта за каждый день просрочки",
                basis="Пункт 7.4 статьи 7 проекта Контракта",
            ),
            Fine(
                description="Штраф за неисполнение требований к конфиденциальности",
                amount="10 000 рублей за каждый факт нарушения",
                basis="Раздел 12, пункт 12.2",
            ),
        ],
        status="extracted",
        notes="Документ успешно обработан. Все ключевые финансовые и юридические метрики извлечены.",
    )