from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Создано",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновлено",
    )

    class Meta:
        abstract = True


class NoteMixin(models.Model):
    note = models.TextField(
        blank=True,
        verbose_name="Примечание",
    )

    class Meta:
        abstract = True


class ActiveMixin(models.Model):
    is_active = models.BooleanField(
        default=True,
        verbose_name="Активна",
    )

    class Meta:
        abstract = True


class Currency(TimeStampedModel, ActiveMixin):
    code = models.CharField(
        max_length=3,
        unique=True,
        verbose_name="Код",
    )
    name = models.CharField(
        max_length=128,
        verbose_name="Название",
    )

    class Meta:
        verbose_name = "Валюта"
        verbose_name_plural = "Валюты"
        ordering = ("code",)

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class ExchangeRateSource(TimeStampedModel, NoteMixin):
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Код",
    )
    name = models.CharField(
        max_length=128,
        verbose_name="Название",
    )
    is_manual = models.BooleanField(
        default=False,
        verbose_name="Ручной источник",
    )

    class Meta:
        verbose_name = "Источник курса"
        verbose_name_plural = "Источники курсов"
        ordering = ("name", "code")

    def __str__(self) -> str:
        return self.name


class ExchangeRate(TimeStampedModel, NoteMixin):
    currency = models.ForeignKey(
        Currency,
        on_delete=models.PROTECT,
        related_name="exchange_rates",
        verbose_name="Валюта",
    )
    rate_date = models.DateField(
        verbose_name="Дата курса",
    )
    rate_to_rub = models.DecimalField(
        max_digits=20,
        decimal_places=8,
        verbose_name="Курс к RUB",
    )
    source = models.ForeignKey(
        ExchangeRateSource,
        on_delete=models.PROTECT,
        related_name="exchange_rates",
        verbose_name="Источник",
    )
    is_manual_override = models.BooleanField(
        default=False,
        verbose_name="Ручная корректировка",
    )

    class Meta:
        verbose_name = "Курс валюты"
        verbose_name_plural = "Курсы валют"
        ordering = ("-rate_date", "currency__code", "source__name")
        constraints = [
            models.UniqueConstraint(
                fields=("currency", "rate_date", "source"),
                name="unique_exchange_rate_per_currency_date_source",
            )
        ]

    def __str__(self) -> str:
        return (
            f"{self.currency.code} {self.rate_date:%Y-%m-%d} "
            f"{self.rate_to_rub} ({self.source.name})"
        )
