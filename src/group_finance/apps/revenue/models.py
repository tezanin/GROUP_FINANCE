from django.core.exceptions import ValidationError
from django.db import models

from group_finance.apps.core.models import Currency, NoteMixin, TimeStampedModel
from group_finance.apps.org.models import Client, Company, Project


class Revenue(TimeStampedModel, NoteMixin):
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="revenues", verbose_name="Компания")
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="revenues", verbose_name="Клиент")
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name="revenues", verbose_name="Проект", null=True, blank=True)
    period_start = models.DateField("Начало периода")
    period_end = models.DateField("Конец периода")
    amount = models.DecimalField("Сумма выручки", max_digits=14, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="revenues", verbose_name="Валюта")
    recognized_date = models.DateField("Дата признания выручки", null=True, blank=True)

    class Meta:
        verbose_name = "Выручка"
        verbose_name_plural = "Выручка"
        ordering = ("-period_start", "-id")

    def __str__(self) -> str:
        return f"{self.company} | {self.client} | {self.amount} {self.currency}"


class Invoice(TimeStampedModel, NoteMixin):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        ISSUED = "issued", "Выставлен"
        PAID = "paid", "Оплачен"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="invoices", verbose_name="Компания")
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="invoices", verbose_name="Клиент")
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name="invoices", verbose_name="Проект", null=True, blank=True)
    number = models.CharField("Номер", max_length=100)
    issue_date = models.DateField("Дата счёта")
    due_date = models.DateField("Срок оплаты", null=True, blank=True)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="invoices", verbose_name="Валюта")
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.DRAFT)
    total_amount = models.DecimalField("Сумма документа", max_digits=14, decimal_places=2)

    class Meta:
        verbose_name = "Счёт"
        verbose_name_plural = "Счета"
        ordering = ("-issue_date", "-id")

    def clean(self):
        super().clean()
        errors = {}
        if self.due_date and self.issue_date and self.due_date < self.issue_date:
            errors["due_date"] = "Срок оплаты не может быть раньше даты счёта."
        if self.project_id and self.company_id and self.project.company_id != self.company_id:
            errors["project"] = "Проект должен относиться к выбранной компании."
        if self.total_amount is not None and self.total_amount <= 0:
            errors["total_amount"] = "Сумма документа должна быть больше нуля."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return self.number


class InvoiceLine(TimeStampedModel):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name="lines", verbose_name="Счёт")
    line_number = models.PositiveIntegerField("Номер строки", default=1)
    description = models.TextField("Описание")
    quantity = models.DecimalField("Количество", max_digits=12, decimal_places=2)
    unit_price = models.DecimalField("Цена", max_digits=14, decimal_places=2)

    class Meta:
        verbose_name = "Строка счёта"
        verbose_name_plural = "Строки счёта"
        ordering = ("invoice", "line_number", "id")

    def clean(self):
        super().clean()
        errors = {}
        if self.quantity is not None and self.quantity <= 0:
            errors["quantity"] = "Количество должно быть больше нуля."
        if self.unit_price is not None and self.unit_price <= 0:
            errors["unit_price"] = "Цена должна быть больше нуля."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.invoice} / {self.line_number}"


class Act(TimeStampedModel, NoteMixin):
    class Status(models.TextChoices):
        DRAFT = "draft", "Черновик"
        SIGNED = "signed", "Подписан"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="acts", verbose_name="Компания")
    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name="acts", verbose_name="Клиент")
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name="acts", verbose_name="Проект", null=True, blank=True)
    number = models.CharField("Номер", max_length=100)
    act_date = models.DateField("Дата акта")
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT, related_name="acts", verbose_name="Валюта")
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.DRAFT)
    total_amount = models.DecimalField("Сумма документа", max_digits=14, decimal_places=2)

    class Meta:
        verbose_name = "Акт"
        verbose_name_plural = "Акты"
        ordering = ("-act_date", "-id")

    def clean(self):
        super().clean()
        errors = {}
        if self.project_id and self.company_id and self.project.company_id != self.company_id:
            errors["project"] = "Проект должен относиться к выбранной компании."
        if self.total_amount is not None and self.total_amount <= 0:
            errors["total_amount"] = "Сумма документа должна быть больше нуля."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return self.number


class ActLine(TimeStampedModel):
    act = models.ForeignKey(Act, on_delete=models.CASCADE, related_name="lines", verbose_name="Акт")
    line_number = models.PositiveIntegerField("Номер строки", default=1)
    description = models.TextField("Описание")
    quantity = models.DecimalField("Количество", max_digits=12, decimal_places=2)
    unit_price = models.DecimalField("Цена", max_digits=14, decimal_places=2)

    class Meta:
        verbose_name = "Строка акта"
        verbose_name_plural = "Строки акта"
        ordering = ("act", "line_number", "id")

    def clean(self):
        super().clean()
        errors = {}
        if self.quantity is not None and self.quantity <= 0:
            errors["quantity"] = "Количество должно быть больше нуля."
        if self.unit_price is not None and self.unit_price <= 0:
            errors["unit_price"] = "Цена должна быть больше нуля."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.act} / {self.line_number}"