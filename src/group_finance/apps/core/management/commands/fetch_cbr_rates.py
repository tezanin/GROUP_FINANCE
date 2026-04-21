from __future__ import annotations

import urllib.request
import xml.etree.ElementTree as ET
from calendar import monthrange
from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError

from group_finance.apps.core.models import Currency, ExchangeRate, ExchangeRateSource

CBR_URL = "http://www.cbr.ru/scripts/XML_dynamic.asp"
SOURCE_CODE = "MANUAL_MONTHLY"
CURRENCIES = {
    "BYN": "R01090B",
    "KZT": "R01335",
}
DEFAULT_START = "2025-01"
QUANT = Decimal("0.00000001")


def parse_month(value: str) -> date:
    try:
        year, month = value.split("-")
        return date(int(year), int(month), 1)
    except (ValueError, AttributeError) as exc:
        raise CommandError(f"Неверный формат месяца: {value!r}, ожидается YYYY-MM") from exc


def iter_months(start: date, end: date):
    cur = start
    while cur <= end:
        yield cur
        if cur.month == 12:
            cur = date(cur.year + 1, 1, 1)
        else:
            cur = date(cur.year, cur.month + 1, 1)


def fetch_records(val_nm_rq: str, first: date, last: date) -> list[tuple[Decimal, Decimal]]:
    url = (
        f"{CBR_URL}?date_req1={first:%d/%m/%Y}"
        f"&date_req2={last:%d/%m/%Y}&VAL_NM_RQ={val_nm_rq}"
    )
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = resp.read()
    root = ET.fromstring(data)
    records: list[tuple[Decimal, Decimal]] = []
    for rec in root.findall("Record"):
        nominal_text = rec.findtext("Nominal") or ""
        value_text = rec.findtext("Value") or ""
        nominal = Decimal(nominal_text.replace(",", "."))
        value = Decimal(value_text.replace(",", "."))
        records.append((nominal, value))
    return records


class Command(BaseCommand):
    help = "Загрузить средние месячные курсы BYN/KZT к RUB с ЦБ РФ."

    def add_arguments(self, parser):
        parser.add_argument("--start", default=DEFAULT_START, help="Начальный месяц YYYY-MM")
        parser.add_argument(
            "--end",
            default=date.today().strftime("%Y-%m"),
            help="Конечный месяц YYYY-MM (включительно)",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Только показать, ничего не писать в БД",
        )

    def handle(self, *args, **options):
        start = parse_month(options["start"])
        end = parse_month(options["end"])
        dry_run: bool = options["dry_run"]

        if end < start:
            raise CommandError(f"--end {end:%Y-%m} раньше --start {start:%Y-%m}")

        try:
            source = ExchangeRateSource.objects.get(code=SOURCE_CODE)
        except ExchangeRateSource.DoesNotExist as exc:
            raise CommandError(
                f"Не найден ExchangeRateSource с code='{SOURCE_CODE}'. "
                "Создайте его вручную и повторите запуск."
            ) from exc

        currencies: dict[str, Currency] = {}
        for code in CURRENCIES:
            try:
                currencies[code] = Currency.objects.get(code=code)
            except Currency.DoesNotExist as exc:
                raise CommandError(f"Не найдена Currency с code='{code}'.") from exc

        today = date.today()

        for month_start in iter_months(start, end):
            last_dom = monthrange(month_start.year, month_start.month)[1]
            month_end = date(month_start.year, month_start.month, last_dom)
            is_current = month_start.year == today.year and month_start.month == today.month
            if is_current:
                month_end = min(month_end, today)

            for code, val_id in CURRENCIES.items():
                currency = currencies[code]
                try:
                    records = fetch_records(val_id, month_start, month_end)
                except Exception as exc:  # noqa: BLE001
                    self.stdout.write(
                        f"[ERR] {code} {month_start:%Y-%m}: {type(exc).__name__}: {exc}"
                    )
                    continue

                if not records:
                    self.stdout.write(
                        f"[SKIP] {code} {month_start:%Y-%m}: нет подневных данных от ЦБ"
                    )
                    continue

                per_unit = [value / nominal for nominal, value in records]
                avg = sum(per_unit, Decimal(0)) / Decimal(len(per_unit))
                rate = avg.quantize(QUANT)

                if not dry_run:
                    ExchangeRate.objects.update_or_create(
                        currency=currency,
                        rate_date=month_start,
                        source=source,
                        defaults={"rate_to_rub": rate},
                    )

                tag = "[DRY]" if dry_run else "[OK]"
                partial = " (partial)" if is_current else ""
                self.stdout.write(
                    f"{tag} {code} {month_start:%Y-%m} "
                    f"({len(records)} дн.) → {rate} RUB{partial}"
                )
