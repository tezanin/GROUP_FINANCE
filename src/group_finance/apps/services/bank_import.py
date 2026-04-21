from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.files import File
from django.db import transaction
from django.utils import timezone

from group_finance.apps.banking.models import BankTransaction
from group_finance.apps.core.models import Currency, ExchangeRate
from group_finance.apps.imports.models import (
    ImportBatch,
    ImportError,
    ImportFile,
    ImportRowRaw,
)
from group_finance.apps.org.models import BankAccount, Company

User = get_user_model()


class BankImportError(Exception):
    """Базовая ошибка импорта банковской выписки.

    code — короткий машинный код ошибки, попадает в ImportError.error_code.
    """

    def __init__(self, message: str, code: str = ""):
        super().__init__(message)
        self.code = code


@dataclass
class ParsedBankRow:
    """Результат разбора одной строки CSV (чистый Python, без БД)."""

    external_id: str          # UUID операции из CSV — идёт в BankTransaction.external_id
    company_name: str         # имя компании из CSV (не код!)
    our_account: str
    doc_number: str
    transaction_date: date    # уже распарсенная дата, не строка
    direction: str            # inflow / outflow (нормализовано)
    amount: Decimal
    currency_code: str
    purpose: str
    raw_payload: dict[str, Any]


REQUIRED_COLUMNS = (
    "company",
    "our_account",
    "date",
    "direction",
    "amount",
    "currency",
)
EXCHANGE_RATE_SOURCE_CODE = "MANUAL_MONTHLY"


def parse_row(row: dict[str, Any]) -> ParsedBankRow:
    """Валидирует и нормализует одну строку CSV. Ничего не пишет в БД."""

    missing_columns = [
        column_name
        for column_name in REQUIRED_COLUMNS
        if not str(row.get(column_name, "")).strip()
    ]
    if missing_columns:
        raise BankImportError(
            f"Не заполнены обязательные поля: {', '.join(missing_columns)}",
            code="missing_column",
        )

    raw_direction = str(row["direction"]).strip().upper()
    if raw_direction == "ПРИХОД":
        normalized_direction = BankTransaction.Direction.INFLOW
    elif raw_direction == "РАСХОД":
        normalized_direction = BankTransaction.Direction.OUTFLOW
    else:
        raise BankImportError(
            "Поле direction должно быть 'ПРИХОД' или 'РАСХОД'",
            code="invalid_direction",
        )

    raw_amount = str(row["amount"]).strip().replace(" ", "").replace(",", ".")
    try:
        amount = Decimal(raw_amount)
    except InvalidOperation as exc:
        raise BankImportError(
            f"Некорректная сумма: {row['amount']}",
            code="invalid_amount",
        ) from exc

    if amount <= 0:
        raise BankImportError(
            "Сумма amount должна быть больше нуля",
            code="invalid_amount",
        )

    raw_date = str(row["date"]).strip()
    try:
        transaction_date = date.fromisoformat(raw_date)
    except ValueError as exc:
        raise BankImportError(
            f"Некорректная дата: {raw_date}. Ожидается формат YYYY-MM-DD",
            code="invalid_date",
        ) from exc

    return ParsedBankRow(
        external_id=str(row.get("id", "")).strip(),
        company_name=str(row["company"]).strip(),
        our_account=str(row["our_account"]).strip(),
        doc_number=str(row.get("doc_number", "")).strip(),
        transaction_date=transaction_date,
        direction=normalized_direction,
        amount=amount,
        currency_code=str(row["currency"]).strip().upper(),
        purpose=str(row["purpose"]).strip(),
        raw_payload=row,
    )


def resolve_company(company_name: str) -> Company:
    """Ищем компанию по short_name (в унифицированном CSV приходит короткое имя)."""
    try:
        return Company.objects.get(short_name=company_name)
    except Company.DoesNotExist as exc:
        raise BankImportError(
            f"Компания с short_name='{company_name}' не найдена",
            code="company_not_found",
        ) from exc
    except Company.MultipleObjectsReturned as exc:
        raise BankImportError(
            f"Найдено несколько компаний с short_name='{company_name}'",
            code="company_ambiguous",
        ) from exc


def resolve_bank_account(company: Company, account_number: str) -> BankAccount:
    try:
        return BankAccount.objects.get(
            company=company,
            account_number=account_number,
        )
    except BankAccount.DoesNotExist as exc:
        raise BankImportError(
            f"Банковский счёт '{account_number}' не найден у компании '{company}'",
            code="bank_account_not_found",
        ) from exc


def resolve_currency(currency_code: str) -> Currency:
    try:
        return Currency.objects.get(code=currency_code)
    except Currency.DoesNotExist as exc:
        raise BankImportError(
            f"Валюта с code='{currency_code}' не найдена",
            code="currency_not_found",
        ) from exc


def resolve_exchange_rate(
    currency: Currency,
    transaction_date: date,
) -> ExchangeRate | None:
    """
    Ищем курс валюты к RUB на месяц операции.

    Возвращает ExchangeRate или None. None — это НЕ ошибка: это штатная
    ситуация «курса на этот месяц ещё нет, amount_rub посчитаем потом».
    Транзакции в RUB — особый случай: курс не нужен, возвращаем None без поиска.
    """
    if currency.code == "RUB":
        return None

    month_start = transaction_date.replace(day=1)
    return ExchangeRate.objects.filter(
        currency=currency,
        rate_date=month_start,
        source__code=EXCHANGE_RATE_SOURCE_CODE,
    ).first()


def build_bank_transaction(parsed: ParsedBankRow) -> BankTransaction:
    """Резолвит FK-справочники и создаёт одну BankTransaction в БД."""

    company = resolve_company(parsed.company_name)
    bank_account = resolve_bank_account(company, parsed.our_account)
    currency = resolve_currency(parsed.currency_code)

    # Защита от повторного импорта того же файла: external_id = UUID из CSV.
    # Это runtime-проверка. В Блоке 1 стоит добавить UniqueConstraint на
    # (company, external_id) в модели BankTransaction.
    if parsed.external_id:
        already_imported = BankTransaction.objects.filter(
            company=company, external_id=parsed.external_id
        ).exists()
        if already_imported:
            raise BankImportError(
                f"Операция с external_id='{parsed.external_id}' уже импортирована",
                code="duplicate",
            )

    # Расчёт amount_rub: для RUB — прямое присвоение, для остальных — по курсу.
    # Если курса на месяц операции нет — amount_rub=NULL, будем добивать через
    # rerun_backfill после дозаливки курсов. Это штатно, не ошибка.
    exchange_rate = resolve_exchange_rate(currency, parsed.transaction_date)
    if currency.code == "RUB":
        amount_rub = parsed.amount
    elif exchange_rate is not None:
        amount_rub = parsed.amount * exchange_rate.rate_to_rub
    else:
        amount_rub = None
        print(
            f"[bank_import] Курс не найден: {currency.code} "
            f"{parsed.transaction_date:%Y-%m} — amount_rub=NULL"
        )

    bank_tx = BankTransaction(
        company=company,
        bank_account=bank_account,
        transaction_date=parsed.transaction_date,
        amount=parsed.amount,
        currency=currency,
        direction=parsed.direction,
        description=parsed.purpose,
        external_id=parsed.external_id,
        amount_rub=amount_rub,
        exchange_rate=exchange_rate,
    )

    # full_clean() прогоняет model.clean() — там проверка, что счёт
    # принадлежит выбранной компании. Хотим, чтобы поймалось до INSERT.
    # Django бросает свой ValidationError — конвертируем в наш BankImportError,
    # чтобы верхний уровень мог поймать одним блоком except.
    try:
        bank_tx.full_clean()
    except DjangoValidationError as exc:
        raise BankImportError(
            f"Ошибка валидации BankTransaction: {exc.messages}",
            code="validation",
        ) from exc

    bank_tx.save()
    return bank_tx


def _process_row(row_raw: ImportRowRaw) -> bool:
    """
    Обрабатывает одну staging-строку: парсит raw_payload → создаёт BankTransaction.

    Используется и первоначальным импортом, и retry. Сохраняет инвариант:
    запись о падении (статус FAILED + ImportError) идёт ВНЕ savepoint'а,
    чтобы она не откатывалась вместе с неудачной попыткой вставки факта.

    Возвращает True при успехе, False при падении.
    """
    try:
        with transaction.atomic():
            parsed = parse_row(row_raw.raw_payload)
            build_bank_transaction(parsed)
    except BankImportError as exc:
        row_raw.status = ImportRowRaw.Status.FAILED
        row_raw.save(update_fields=["status", "updated_at"])
        ImportError.objects.create(
            batch=row_raw.batch,
            import_file=row_raw.import_file,
            import_row=row_raw,
            error_code=exc.code,
            message=str(exc),
        )
        return False
    else:
        row_raw.status = ImportRowRaw.Status.PROCESSED
        row_raw.save(update_fields=["status", "updated_at"])
        return True


@transaction.atomic
def import_bank_statement_csv(
    file_path: str | Path,
    user: User | None = None,
) -> ImportBatch:
    """
    Импорт банковской выписки из унифицированного CSV.
    (docstring тот же, что был)
    """

    path = Path(file_path)
    if not path.exists():
        raise BankImportError(f"Файл не найден: {path}", code="file_not_found")

    started_at = timezone.now()

    batch = ImportBatch.objects.create(
        import_type="bank_statement",
        status=ImportBatch.Status.PROCESSING,
        started_at=started_at,
        created_by=user,
    )

    import_file = ImportFile(
        batch=batch,
        original_name=path.name,
        size_bytes=path.stat().st_size,
        status=ImportFile.Status.NEW,
        uploaded_by=user,
    )
    with path.open("rb") as fh:
        import_file.file.save(path.name, File(fh), save=True)

    failed_rows = 0

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row_number, row in enumerate(reader, start=1):
            row_raw = ImportRowRaw.objects.create(
                batch=batch,
                import_file=import_file,
                row_number=row_number,
                raw_payload=row,
                status=ImportRowRaw.Status.NEW,
            )
            if not _process_row(row_raw):
                failed_rows += 1

    if failed_rows == 0:
        batch.status = ImportBatch.Status.COMPLETED
        import_file.status = ImportFile.Status.PARSED
    else:
        batch.status = ImportBatch.Status.FAILED
        import_file.status = ImportFile.Status.FAILED

    batch.finished_at = timezone.now()
    batch.save(update_fields=["status", "finished_at", "updated_at"])
    import_file.save(update_fields=["status", "updated_at"])

    return batch


@transaction.atomic
def retry_failed_rows(batch_id: int) -> dict[str, int]:
    """
    Перепрогоняет failed-строки существующего пакета, не читая CSV заново.

    Используется после того, как починили справочник (добавили BankAccount,
    Currency и т.п.): вместо перезагрузки всего файла — добиваем только то,
    что упало.

    Старые ImportError остаются как исторический лог (договор: разрешение
    ошибок делаем в отдельном блоке позже). При повторном падении строки
    создаётся новая ImportError.

    Возвращает метрики прогона для печати в shell.
    """
    batch = ImportBatch.objects.get(pk=batch_id)

    # list() — чтобы queryset материализовался ДО того, как мы начнём менять
    # статусы внутри цикла. Иначе фильтр «status=FAILED» может пересчитаться
    # и поведение станет неочевидным.
    failed_rows = list(
        ImportRowRaw.objects
        .filter(batch=batch, status=ImportRowRaw.Status.FAILED)
        .select_related("batch", "import_file")
    )

    total_retried = len(failed_rows)
    processed = 0
    still_failed = 0

    for row_raw in failed_rows:
        if _process_row(row_raw):
            processed += 1
        else:
            still_failed += 1

    # Пересчёт итогового статуса батча по фактическим статусам ВСЕХ его строк.
    # Не опираемся на счётчики из цикла: в батче могли быть и другие строки,
    # кроме перепрогнанных.
    has_failed_rows = ImportRowRaw.objects.filter(
        batch=batch,
        status=ImportRowRaw.Status.FAILED,
    ).exists()

    batch.status = (
        ImportBatch.Status.FAILED if has_failed_rows
        else ImportBatch.Status.COMPLETED
    )
    batch.save(update_fields=["status", "updated_at"])

    return {
        "total_retried": total_retried,
        "processed": processed,
        "still_failed": still_failed,
    }
