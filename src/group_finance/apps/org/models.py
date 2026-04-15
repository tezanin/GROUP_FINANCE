from django.db import models

from group_finance.apps.core.models import ActiveMixin, NoteMixin, TimeStampedModel


class Company(TimeStampedModel, NoteMixin, ActiveMixin):
    class CompanyType(models.TextChoices):
        LEGAL_ENTITY = "legal_entity", "Юрлицо"
        INDIVIDUAL = "individual", "Физлицо/ИП"

    name = models.CharField("Название", max_length=255)
    short_name = models.CharField("Краткое название", max_length=100, blank=True)
    company_type = models.CharField(
        "Тип компании",
        max_length=30,
        choices=CompanyType.choices,
        default=CompanyType.LEGAL_ENTITY,
    )
    tax_id = models.CharField("УНП/ИНН/БИН", max_length=50, blank=True)
    registration_country = models.CharField("Страна регистрации", max_length=2)
    base_currency = models.ForeignKey(
        "core.Currency",
        on_delete=models.PROTECT,
        related_name="companies",
        verbose_name="Базовая валюта",
    )

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"
        ordering = ("name",)

    def __str__(self) -> str:
        return self.short_name or self.name


class BusinessDirection(TimeStampedModel, NoteMixin, ActiveMixin):
    name = models.CharField("Название", max_length=255)
    code = models.CharField("Код", max_length=50, unique=True)
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="business_directions",
        verbose_name="Компания",
    )

    class Meta:
        verbose_name = "Направление бизнеса"
        verbose_name_plural = "Направления бизнеса"
        ordering = ("name",)
        constraints = [
            models.UniqueConstraint(
                fields=("company", "name"),
                name="unique_business_direction_name_per_company",
            )
        ]

    def __str__(self) -> str:
        return self.name
