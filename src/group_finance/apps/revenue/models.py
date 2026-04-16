from django.db import models

from group_finance.apps.core.models import NoteMixin, TimeStampedModel
from group_finance.apps.core.models import Currency
from group_finance.apps.org.models import Client, Company, Project


class Revenue(TimeStampedModel, NoteMixin):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="revenues",
        verbose_name="Компания",
    )

    client = models.ForeignKey(
        Client,
        on_delete=models.PROTECT,
        related_name="revenues",
        verbose_name="Клиент",
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name="revenues",
        verbose_name="Проект",
        null=True,
        blank=True,
    )

    period_start = models.DateField("Начало периода")
    period_end = models.DateField("Конец периода")

    amount = models.DecimalField(
        "Сумма выручки",
        max_digits=14,
        decimal_places=2,
    )

    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="revenues",
        verbose_name="Валюта",
    )

    recognized_date = models.DateField(
        "Дата признания выручки",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Выручка"
        verbose_name_plural = "Выручка"
        ordering = ("-period_start", "-id")

    def __str__(self) -> str:
        return f"{self.company} | {self.client} | {self.amount} {self.currency}"
