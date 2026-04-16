from django.db import models

from group_finance.apps.core.models import NoteMixin, TimeStampedModel
from group_finance.apps.core.models import Currency
from group_finance.apps.org.models import BusinessDirection, Company, Project


class ExpenseCategory(TimeStampedModel):
    name = models.CharField("Название", max_length=255)
    code = models.CharField("Код", max_length=50, unique=True)

    class Meta:
        verbose_name = "Категория расхода"
        verbose_name_plural = "Категории расходов"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class Expense(TimeStampedModel, NoteMixin):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="expenses",
        verbose_name="Компания",
    )

    category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name="expenses",
        verbose_name="Категория",
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name="expenses",
        verbose_name="Проект",
        null=True,
        blank=True,
    )

    business_direction = models.ForeignKey(
        BusinessDirection,
        on_delete=models.PROTECT,
        related_name="expenses",
        verbose_name="Направление бизнеса",
        null=True,
        blank=True,
    )

    period_start = models.DateField("Начало периода")
    period_end = models.DateField("Конец периода")

    amount = models.DecimalField(
        "Сумма расхода",
        max_digits=14,
        decimal_places=2,
    )

    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="expenses",
        verbose_name="Валюта",
    )

    recognized_date = models.DateField(
        "Дата признания расхода",
        null=True,
        blank=True,
    )

    is_operational = models.BooleanField(
        "Операционный расход",
        default=True,
    )

    class Meta:
        verbose_name = "Расход"
        verbose_name_plural = "Расходы"
        ordering = ("-period_start", "-id")

    def __str__(self) -> str:
        return f"{self.company} | {self.category} | {self.amount} {self.currency}"
