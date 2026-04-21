from django.db.models import Count, Q, Sum

from group_finance.apps.banking.models import BankTransaction

total = BankTransaction.objects.count()
with_rub = BankTransaction.objects.filter(amount_rub__isnull=False).count()
without_rub = BankTransaction.objects.filter(amount_rub__isnull=True).count()

print(f"Всего транзакций: {total}")
print(f"С amount_rub:     {with_rub}")
print(f"Без amount_rub:   {without_rub}")
print()
print("Разбивка по валютам:")
by_currency = (
    BankTransaction.objects
    .values("currency__code")
    .annotate(
        cnt=Count("id"),
        with_rub_cnt=Count("id", filter=Q(amount_rub__isnull=False)),
        sum_rub=Sum("amount_rub"),
    )
    .order_by("currency__code")
)
for row in by_currency:
    print(
        f"  {row['currency__code']}: всего {row['cnt']}, "
        f"с amount_rub {row['with_rub_cnt']}, сумма RUB = {row['sum_rub']}"
    )
