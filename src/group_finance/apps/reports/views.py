from collections import defaultdict

from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from django.shortcuts import render

from group_finance.apps.banking.models import BankTransaction


def cashflow_report(request):
    year = 2025

    queryset = BankTransaction.objects.filter(
        transaction_date__year=year,
    )

    rows = (
        queryset
        .annotate(month=TruncMonth("transaction_date"))
        .values(
            "company__short_name",
            "currency__code",
            "month",
        )
        .annotate(
            inflow_orig=Sum("amount", filter=Q(direction="inflow")),
            outflow_orig=Sum("amount", filter=Q(direction="outflow")),
            inflow_rub=Sum("amount_rub", filter=Q(direction="inflow")),
            outflow_rub=Sum("amount_rub", filter=Q(direction="outflow")),
        )
        .order_by("company__short_name", "currency__code", "month")
    )

    # Группируем строки по компаниям для удобства шаблона
    rows_by_company = defaultdict(list)
    for row in rows:
        company_name = row["company__short_name"]
        rows_by_company[company_name].append({
            "currency": row["currency__code"],
            "month": row["month"],
            "inflow_orig": row["inflow_orig"],
            "outflow_orig": row["outflow_orig"],
            "inflow_rub": row["inflow_rub"],
            "outflow_rub": row["outflow_rub"],
        })

    context = {
        "year": year,
        "rows_by_company": dict(rows_by_company),
        "total_rows": len(rows),
    }

    return render(request, "reports/cashflow.html", context)
