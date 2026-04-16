from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from group_finance.apps.core.models import NoteMixin, TimeStampedModel
from group_finance.apps.org.models import Company


class ImportBatch(TimeStampedModel, NoteMixin):
    class Status(models.TextChoices):
        NEW = "new", "Новый"
        PROCESSING = "processing", "В обработке"
        COMPLETED = "completed", "Завершён"
        FAILED = "failed", "Завершён с ошибкой"

    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="import_batches",
        verbose_name="Компания",
        null=True,
        blank=True,
    )
    import_type = models.CharField("Тип импорта", max_length=100)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.NEW)
    started_at = models.DateTimeField("Начат", null=True, blank=True)
    finished_at = models.DateTimeField("Завершён", null=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="created_import_batches",
        verbose_name="Кто создал",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Пакет импорта"
        verbose_name_plural = "Пакеты импорта"
        ordering = ("-created_at",)

    def clean(self):
        super().clean()
        if self.started_at and self.finished_at and self.finished_at < self.started_at:
            raise ValidationError({"finished_at": "Время завершения не может быть раньше времени начала."})

    def __str__(self) -> str:
        return f"{self.import_type} #{self.pk}"


class ImportFile(TimeStampedModel, NoteMixin):
    class Status(models.TextChoices):
        NEW = "new", "Новый"
        PARSED = "parsed", "Разобран"
        FAILED = "failed", "Ошибка"

    batch = models.ForeignKey(ImportBatch, on_delete=models.CASCADE, related_name="files", verbose_name="Пакет импорта")
    file = models.FileField("Файл", upload_to="imports/")
    original_name = models.CharField("Имя файла", max_length=255)
    mime_type = models.CharField("MIME type", max_length=100, blank=True)
    size_bytes = models.PositiveBigIntegerField("Размер в байтах", null=True, blank=True)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.NEW)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="import_files",
        verbose_name="Кто загрузил",
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = "Файл импорта"
        verbose_name_plural = "Файлы импорта"
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return self.original_name


class ImportRowRaw(TimeStampedModel):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        PROCESSED = "processed", "Обработана"
        FAILED = "failed", "Ошибка"

    batch = models.ForeignKey(ImportBatch, on_delete=models.CASCADE, related_name="rows_raw", verbose_name="Пакет импорта")
    import_file = models.ForeignKey(ImportFile, on_delete=models.CASCADE, related_name="rows_raw", verbose_name="Файл импорта")
    row_number = models.PositiveIntegerField("Номер строки")
    raw_payload = models.JSONField("Сырые данные", default=dict, blank=True)
    status = models.CharField("Статус", max_length=20, choices=Status.choices, default=Status.NEW)

    class Meta:
        verbose_name = "Сырая строка импорта"
        verbose_name_plural = "Сырые строки импорта"
        ordering = ("import_file", "row_number")
        constraints = [models.UniqueConstraint(fields=("import_file", "row_number"), name="unique_import_row_number_per_file")]

    def clean(self):
        super().clean()
        if self.import_file_id and self.batch_id and self.import_file.batch_id != self.batch_id:
            raise ValidationError({"import_file": "Файл импорта должен относиться к выбранному пакету."})

    def __str__(self) -> str:
        return f"Row #{self.row_number} ({self.import_file})"


class ImportError(TimeStampedModel):
    class Level(models.TextChoices):
        ERROR = "error", "Ошибка"
        WARNING = "warning", "Предупреждение"

    batch = models.ForeignKey(ImportBatch, on_delete=models.CASCADE, related_name="errors", verbose_name="Пакет импорта")
    import_file = models.ForeignKey(ImportFile, on_delete=models.CASCADE, related_name="errors", verbose_name="Файл импорта", null=True, blank=True)
    import_row = models.ForeignKey(ImportRowRaw, on_delete=models.CASCADE, related_name="errors", verbose_name="Сырая строка", null=True, blank=True)
    error_code = models.CharField("Код ошибки", max_length=100, blank=True)
    message = models.TextField("Сообщение")
    level = models.CharField("Уровень", max_length=20, choices=Level.choices, default=Level.ERROR)

    class Meta:
        verbose_name = "Ошибка импорта"
        verbose_name_plural = "Ошибки импорта"
        ordering = ("-created_at",)

    def clean(self):
        super().clean()
        errors = {}
        if self.import_file_id and self.batch_id and self.import_file.batch_id != self.batch_id:
            errors["import_file"] = "Файл импорта должен относиться к выбранному пакету."
        if self.import_row_id:
            if self.batch_id and self.import_row.batch_id != self.batch_id:
                errors["import_row"] = "Строка импорта должна относиться к выбранному пакету."
            if self.import_file_id and self.import_row.import_file_id != self.import_file_id:
                errors["import_row"] = "Строка импорта должна относиться к выбранному файлу."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return self.error_code or f"Import error #{self.pk}"