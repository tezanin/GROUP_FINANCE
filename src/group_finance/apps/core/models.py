from django.conf import settings
from django.db import models
from group_finance.apps.core.utils.code_generator import generate_unique_code

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

class CodeMixin(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        code_value = getattr(self, "code", None)
        name_value = getattr(self, "name", None)

        if (code_value is None or code_value == "") and name_value:
            self.code = generate_unique_code(
                model_class=type(self),
                name=name_value,
                instance_pk=self.pk,
            )

        self.full_clean()
        super().save(*args, **kwargs)
        
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

class Comment(TimeStampedModel, NoteMixin, ActiveMixin):
    content = models.TextField("Текст комментария")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="comments",
        verbose_name="Автор",
    )

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment #{self.pk}"


class Attachment(TimeStampedModel, NoteMixin, ActiveMixin):
    file = models.FileField("Файл", upload_to="attachments/")
    original_name = models.CharField("Имя файла", max_length=255)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="attachments",
        verbose_name="Кто загрузил",
    )
    mime_type = models.CharField("MIME type", max_length=100, blank=True)
    size_bytes = models.PositiveBigIntegerField("Размер в байтах", null=True, blank=True)

    class Meta:
        verbose_name = "Вложение"
        verbose_name_plural = "Вложения"
        ordering = ["-created_at"]

    def __str__(self):
        return self.original_name


class AuditLog(TimeStampedModel):
    entity_type = models.CharField("Тип сущности", max_length=100)
    entity_id = models.CharField("ID сущности", max_length=64)
    action = models.CharField("Действие", max_length=50)
    payload = models.JSONField("Данные", default=dict, blank=True)
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="audit_logs",
        verbose_name="Пользователь",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Запись аудита"
        verbose_name_plural = "Журнал аудита"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.entity_type}:{self.entity_id} [{self.action}]"

