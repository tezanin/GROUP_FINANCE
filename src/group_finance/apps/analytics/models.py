from django.core.exceptions import ValidationError
from django.db import models

from group_finance.apps.core.models import Currency, TimeStampedModel
from group_finance.apps.expenses.models import ExpenseCategory
from group_finance.apps.org.models import BusinessDirection, Company, Project


class AnalyticObjectType(models.TextChoices):
    BANK_TRANSACTION = "bank_transaction", "Банковская операция"
    TIMESHEET_ENTRY = "timesheet_entry", "Запись таймшита"
    PAYROLL = "payroll", "Начисление зарплаты"
    PAYROLL_PAYMENT = "payroll_payment", "Выплата зарплаты"
    REVENUE = "revenue", "Выручка"
    INVOICE = "invoice", "Счёт"
    ACT = "act", "Акт"
    EXPENSE = "expense", "Расход"
    ALLOCATION = "allocation", "Разнесение"
    ADJUSTMENT = "adjustment", "Корректировка"


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
    data = models.JSONField("Данные отчёта", default=dict, blank=True)
    generated_at = models.DateTimeField("Сгенерировано", auto_now_add=True)

    class Meta:
        verbose_name = "Снимок отчёта"
        verbose_name_plural = "Снимки отчётов"
        ordering = ("-period_start", "-generated_at")

    def __str__(self) -> str:
        return f"{self.company} | {self.report_type} | {self.period_start} - {self.period_end}"


class Allocation(TimeStampedModel):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="allocations",
        verbose_name="Компания",
    )
    source_type = models.CharField(
        "Тип источника",
        max_length=30,
        choices=AnalyticObjectType.choices,
    )
    source_id = models.PositiveBigIntegerField("ID источника")
    allocation_date = models.DateField("Дата разнесения")
    amount = models.DecimalField("Сумма", max_digits=14, decimal_places=2)
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="allocations",
        verbose_name="Валюта",
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.PROTECT,
        related_name="allocations",
        verbose_name="Проект",
        null=True,
        blank=True,
    )
    business_direction = models.ForeignKey(
        BusinessDirection,
        on_delete=models.PROTECT,
        related_name="allocations",
        verbose_name="Направление бизнеса",
        null=True,
        blank=True,
    )
    expense_category = models.ForeignKey(
        ExpenseCategory,
        on_delete=models.PROTECT,
        related_name="allocations",
        verbose_name="Категория расхода",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Разнесение"
        verbose_name_plural = "Разнесения"
        ordering = ("-allocation_date", "-id")

    def clean(self):
        super().clean()
        errors = {}

        if self.amount is not None and self.amount <= 0:
            errors["amount"] = "Сумма разнесения должна быть больше нуля."

        if self.project_id and self.company_id and self.project.company_id != self.company_id:
            errors["project"] = "Проект должен относиться к выбранной компании."

        if (
            self.business_direction_id
            and self.company_id
            and self.business_direction.company_id != self.company_id
        ):
            errors["business_direction"] = "Направление бизнеса должно относиться к выбранной компании."

        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.source_type}:{self.source_id} | {self.amount} {self.currency}"


class Adjustment(TimeStampedModel):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="adjustments",
        verbose_name="Компания",
    )
    target_type = models.CharField(
        "Тип объекта",
        max_length=30,
        choices=AnalyticObjectType.choices,
    )
    target_id = models.PositiveBigIntegerField("ID объекта")
    adjustment_date = models.DateField("Дата корректировки")
    amount = models.DecimalField("Сумма", max_digits=14, decimal_places=2)
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="adjustments",
        verbose_name="Валюта",
    )
    reason = models.TextField("Причина")

    class Meta:
        verbose_name = "Корректировка"
        verbose_name_plural = "Корректировки"
        ordering = ("-adjustment_date", "-id")

    def clean(self):
        super().clean()
        errors = {}

        if self.amount is not None and self.amount == 0:
            errors["amount"] = "Сумма корректировки не может быть равна нулю."

        if not (self.reason or "").strip():
            errors["reason"] = "Причина корректировки обязательна."

        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.target_type}:{self.target_id} | {self.amount}"


class ReconciliationRecord(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Не сверено"
        MATCHED = "matched", "Сверено"
        MISMATCH = "mismatch", "Есть расхождение"

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="reconciliation_records",
        verbose_name="Компания",
    )
    left_source_type = models.CharField(
        "Левый источник",
        max_length=30,
        choices=AnalyticObjectType.choices,
    )
    left_source_id = models.PositiveBigIntegerField("ID левого источника")
    right_source_type = models.CharField(
        "Правый источник",
        max_length=30,
        choices=AnalyticObjectType.choices,
    )
    right_source_id = models.PositiveBigIntegerField("ID правого источника")
    status = models.CharField(
        "Статус",
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    difference_amount = models.DecimalField("Разница", max_digits=14, decimal_places=2)
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="reconciliation_records",
        verbose_name="Валюта",
    )
    checked_at = models.DateTimeField("Проверено", null=True, blank=True)

    class Meta:
        verbose_name = "Запись сверки"
        verbose_name_plural = "Записи сверки"
        ordering = ("-created_at",)

    def clean(self):
        super().clean()
        errors = {}

        if self.difference_amount is not None and self.difference_amount < 0:
            errors["difference_amount"] = "Разница не может быть отрицательной."

        if (
            self.left_source_type == self.right_source_type
            and self.left_source_id
            and self.left_source_id == self.right_source_id
        ):
            errors["right_source_id"] = "Нельзя сверять объект сам с собой."

        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.left_source_type}:{self.left_source_id} <> {self.right_source_type}:{self.right_source_id}"