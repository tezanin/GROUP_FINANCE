from django.db import models

from group_finance.apps.core.models import TimeStampedModel
from group_finance.apps.people.models import Employee
from group_finance.apps.core.models import Currency


class SalaryRate(TimeStampedModel):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="salary_rates",
        verbose_name="Сотрудник",
    )

    amount = models.DecimalField(
        "Ставка",
        max_digits=12,
        decimal_places=2,
    )

    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="salary_rates",
        verbose_name="Валюта",
    )

    effective_from = models.DateField("Действует с")

    class Meta:
        verbose_name = "Ставка сотрудника"
        verbose_name_plural = "Ставки сотрудников"
        ordering = ("-effective_from",)

    def __str__(self):
        return f"{self.employee} | {self.amount} {self.currency}"


class Payroll(TimeStampedModel):
    employee = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="payrolls",
        verbose_name="Сотрудник",
    )

    period_start = models.DateField("Начало периода")
    period_end = models.DateField("Конец периода")

    amount = models.DecimalField(
        "Сумма",
        max_digits=14,
        decimal_places=2,
    )

    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="payrolls",
        verbose_name="Валюта",
    )

    is_paid = models.BooleanField("Выплачено", default=False)

    class Meta:
        verbose_name = "Начисление зарплаты"
        verbose_name_plural = "Начисления зарплаты"
        ordering = ("-period_start",)

    def __str__(self):
        return f"{self.employee} | {self.period_start} - {self.period_end} | {self.amount}"
