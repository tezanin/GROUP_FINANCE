from __future__ import annotations

import csv
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any

from django.contrib.auth import get_user_model
from django.db import transaction

from group_finance.apps.banking.models import BankTransaction
from group_finance.apps.core.models import Currency
from group_finance.apps.imports.models import ImportBatch, ImportError, ImportFile, ImportRowRaw
from group_finance.apps.org.models import BankAccount, Company

User = get_user_model()


class BankImportError(Exception):
    """Базовая ошибка импорта банковской выписки."""


@dataclass
class ParsedBankRow:
    company_code: str
    our_account: str
    doc_number: str
    transaction_date: str
    direction: str
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
    "purpose",
)


def parse_row(row: dict[str, Any]) -> ParsedBankRow:
    missing_columns = [
        column_name
        for column_name in REQUIRED_COLUMNS
        if not str(row.get(column_name, "")).strip()
    ]
    if missing_columns:
        raise BankImportError(
            f"Не заполнены обязательные поля: {', '.join(missing_columns)}"
        )

    raw_direction = str(row["direction"]).strip().upper()
    if raw_direction == "ПРИХОД":
        normalized_direction = "inflow"
    elif raw_direction == "РАСХОД":
        normalized_direction = "outflow"
    else:
        raise BankImportError(
            "Поле direction должно быть 'ПРИХОД' или 'РАСХОД'"
        )

    raw_amount = str(row["amount"]).strip().replace(" ", "").replace(",", ".")
    try:
        amount = Decimal(raw_amount)
    except InvalidOperation as exc:
        raise BankImportError(f"Некорректная сумма: {row['amount']}") from exc

    if amount <= 0:
        raise BankImportError("Сумма amount должна быть больше нуля")

    return ParsedBankRow(
        company_code=str(row["company"]).strip(),
        our_account=str(row["our_account"]).strip(),
        doc_number=str(row.get("doc_number", "")).strip(),
        transaction_date=str(row["date"]).strip(),
        direction=normalized_direction,
        amount=amount,
        currency_code=str(row["currency"]).strip().upper(),
        purpose=str(row["purpose"]).strip(),
        raw_payload=row,
    )

def resolve_company(company_code: str) -> Company:
    try:
        return Company.objects.get(code=company_code)
    except Company.DoesNotExist as exc:
        raise BankImportError(
            f"Компания с code='{company_code}' не найдена"
        ) from exc


def resolve_bank_account(company: Company, account_number: str) -> BankAccount:
    try:
        return BankAccount.objects.get(
            company=company,
            account_number=account_number,
        )
    except BankAccount.DoesNotExist as exc:
        raise BankImportError(
            f"Банковский счёт '{account_number}' не найден у компании '{company}'"
        ) from exc


def resolve_currency(currency_code: str) -> Currency:
    try:
        return Currency.objects.get(code=currency_code)
    except Currency.DoesNotExist as exc:
        raise BankImportError(
            f"Валюта с code='{currency_code}' не найдена"
        ) from exc

@transaction.atomic
def import_bank_statement_csv(
    file_path: str | Path,
    user: User | None = None,
) -> ImportBatch:
    """
    Импортирует банковскую выписку из CSV.

    На MVP-этапе функция:
    1. создаёт ImportBatch
    2. создаёт ImportFile
    3. читает строки CSV
    4. сохраняет каждую строку в ImportRowRaw
    5. позже будет создавать BankTransaction или ImportError
    """
    path = Path(file_path)

    if not path.exists():
        raise BankImportError(f"Файл не найден: {path}")

    batch = ImportBatch.objects.create(
        import_type="bank_statement",
        status="processing",
        created_by=user,
    )

    import_file = ImportFile.objects.create(
        batch=batch,
        original_name=path.name,
        status="processing",
        uploaded_by=user,
    )

    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)

        for row_number, row in enumerate(reader, start=1):
            ImportRowRaw.objects.create(
                batch=batch,
                import_file=import_file,
                row_number=row_number,
                raw_payload=row,
                status="new",
            )

    batch.status = "completed"
    batch.save(update_fields=["status", "updated_at"])

    import_file.status = "completed"
    import_file.save(update_fields=["status", "updated_at"])

    return batch