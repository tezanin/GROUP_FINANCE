from django.core.exceptions import ValidationError
from django.db import models

from group_finance.apps.core.models import Currency, NoteMixin, TimeStampedModel
from group_finance.apps.org.models import Company


class SalaryRate(TimeStampedModel):
    engagement = models.ForeignKey(
        "people.PersonCompanyEngagement",
        on_delete=models.CASCADE,
        related_name="salary_rates",
        verbose_name="Занятость",
    )
    amount = models.DecimalField("Ставка", max_digits=12, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="salary_rates", verbose_name="Валюта")
    effective_from = models.DateField("Действует с")

    class Meta:
        verbose_name = "Ставка сотрудника"
        verbose_name_plural = "Ставки сотрудников"
        ordering = ("-effective_from",)

    def __str__(self):
        return f"{self.engagement} | {self.amount} {self.currency}"


class Payroll(TimeStampedModel):
    engagement = models.ForeignKey(
        "people.PersonCompanyEngagement",
        on_delete=models.CASCADE,
        related_name="payrolls",
        verbose_name="Занятость",
    )
    period_start = models.DateField("Начало периода")
    period_end = models.DateField("Конец периода")
    amount = models.DecimalField("Сумма", max_digits=14, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="payrolls", verbose_name="Валюта")
    is_paid = models.BooleanField("Выплачено", default=False)

    class Meta:
        verbose_name = "Начисление зарплаты"
        verbose_name_plural = "Начисления зарплаты"
        ordering = ("-period_start",)

    def clean(self):
        super().clean()
        if self.period_start and self.period_end and self.period_end < self.period_start:
            raise ValidationError({"period_end": "Дата окончания периода не может быть раньше даты начала."})

    def __str__(self):
        return f"{self.engagement} | {self.period_start} - {self.period_end} | {self.amount}"


class PayrollPayment(TimeStampedModel, NoteMixin):
    class Status(models.TextChoices):
        PLANNED = "planned", "Запланирован"
        PAID = "paid", "Выплачен"
        FAILED = "failed", "Ошибка"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="payroll_payments", verbose_name="Компания")
    engagement = models.ForeignKey(
        "people.PersonCompanyEngagement",
        on_delete=models.CASCADE,
        related_name="payroll_payments",
        verbose_name="Занятость",
    )
    payroll = models.ForeignKey(Payroll, on_delete=models.PROTECT, related_name="payments", verbose_name="Начисление", null=True, blank=True)
    payment_date = models.DateField("Дата выплаты")
    amount = models.DecimalField("Сумма", max_digits=14, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="payroll_payments", verbose_name="Валюта")
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.PLANNED)

    class Meta:
        verbose_name = "Выплата зарплаты"
        verbose_name_plural = "Выплаты зарплаты"
        ordering = ("-payment_date", "-id")

    def clean(self):
        super().clean()
        errors = {}
        if self.amount is not None and self.amount <= 0:
            errors["amount"] = "Сумма выплаты должна быть больше нуля."
        if self.engagement_id and self.company_id and self.engagement.company_id != self.company_id:
            errors["engagement"] = "Занятость должна относиться к выбранной компании."
        if self.payroll_id:
            if self.engagement_id and self.payroll.engagement_id != self.engagement_id:
                errors["payroll"] = "Начисление должно относиться к выбранной занятости."
            if self.currency_id and self.payroll.currency_id != self.currency_id:
                errors["currency"] = "Валюта выплаты должна совпадать с валютой начисления."
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.engagement} | {self.payment_date} | {self.amount}"
