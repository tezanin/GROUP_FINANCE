from collections import defaultdict

from django.db import migrations


SOURCE_CODE = "MANUAL_MONTHLY"


def backfill_amount_rub(apps, schema_editor):
    BankTransaction = apps.get_model("banking", "BankTransaction")
    ExchangeRate = apps.get_model("core", "ExchangeRate")

    rub_direct = 0
    recalculated = 0
    missing = defaultdict(int)
    total_touched = 0

    qs = BankTransaction.objects.filter(amount_rub__isnull=True).select_related("currency")

    for tx in qs.iterator():
        total_touched += 1

        if tx.currency.code == "RUB":
            tx.amount_rub = tx.amount
            tx.exchange_rate = None
            tx.save(update_fields=["amount_rub", "exchange_rate"])
            rub_direct += 1
            continue

        month_start = tx.transaction_date.replace(day=1)
        rate = (
            ExchangeRate.objects.filter(
                currency=tx.currency,
                rate_date=month_start,
                source__code=SOURCE_CODE,
            )
            .first()
        )

        if rate is None:
            missing[(tx.currency.code, month_start)] += 1
            continue

        tx.amount_rub = tx.amount * rate.rate_to_rub
        tx.exchange_rate = rate
        tx.save(update_fields=["amount_rub", "exchange_rate"])
        recalculated += 1

    print("[backfill amount_rub]")
    print(f"  RUB напрямую: {rub_direct}")
    print(f"  Пересчитано по курсу: {recalculated}")
    if missing:
        print("  Без курса (оставлены NULL):")
        for (code, month), cnt in sorted(missing.items()):
            print(f"    {code} {month:%Y-%m}: {cnt}")
    else:
        print("  Без курса: 0")
    print(f"  Всего затронуто: {total_touched}")


class Migration(migrations.Migration):

    dependencies = [
        ("banking", "0002_banktransaction_amount_rub_and_more"),
    ]

    operations = [
        migrations.RunPython(backfill_amount_rub, migrations.RunPython.noop),
    ]
