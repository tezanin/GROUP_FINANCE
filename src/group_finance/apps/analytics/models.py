from django.db import models

from group_finance.apps.core.models import TimeStampedModel
from group_finance.apps.org.models import Company, Project


class ReportSnapshot(TimeStampedModel):
    class ReportType(models.TextChoices):
        CASHFLOW = "cashflow", "Cash Flow"
        PNL = "pnl", "P&L"
        UNIT_ECONOMICS = "unit_economics", "Unit Economics"

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="report_snapshots",
        verbose_name="Компания",
    )

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="report_snapshots",
        verbose_name="Проект",
        null=True,
        blank=True,
    )

    report_type = models.CharField(
        "Тип отчёта",
        max_length=30,
        choices=ReportType.choices,
    )

    period_start = models.DateField("Начало периода")
    period_end = models.DateField("Конец периода")

    data = models.JSONField(
        "Данные отчёта",
        default=dict,
        blank=True,
    )

    generated_at = models.DateTimeField(
        "Сгенерировано",
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Снимок отчёта"
        verbose_name_plural = "Снимки отчётов"
        ordering = ("-period_start", "-generated_at")

    def __str__(self) -> str:
        return f"{self.company} | {self.report_type} | {self.period_start} - {self.period_end}"
