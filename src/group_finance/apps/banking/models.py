from django.core.exceptions import ValidationError
from django.db import models

from group_finance.apps.core.models import Currency, NoteMixin, TimeStampedModel
from group_finance.apps.org.models import BankAccount, Company


class BankTransaction(TimeStampedModel, NoteMixin):
    class Direction(models.TextChoices):
        INFLOW = "inflow", "Поступление"
        OUTFLOW = "outflow", "Списание"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="bank_transactions", verbose_name="Компания")
    bank_account = models.ForeignKey(BankAccount, on_delete=models.PROTECT, related_name="transactions", verbose_name="Банковский счёт")
    transaction_date = models.DateField("Дата операции")
    amount = models.DecimalField("Сумма", max_digits=14, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="bank_transactions", verbose_name="Валюта")
    direction = models.CharField("Направление", max_length=20, choices=Direction.choices)
    description = models.TextField("Описание", blank=True)
    external_id = models.CharField("Внешний ID", max_length=255, blank=True)

    class Meta:
        verbose_name = "Банковская операция"
        verbose_name_plural = "Банковские операции"
        ordering = ("-transaction_date", "-id")

    def clean(self):
        super().clean()
        errors = {}
        if self.amount is not None and self.amount <= 0:
            errors["amount"] = "Сумма операции должна быть больше нуля."
        if self.bank_account_id and self.company_id and self.bank_account.company_id != self.company_id:
            errors["bank_account"] = "Банковский счёт должен относиться к выбранной компании."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.company} | {self.transaction_date} | {self.amount} {self.currency}"