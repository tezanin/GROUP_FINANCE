from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q

from group_finance.apps.core.models import ActiveMixin, NoteMixin, TimeStampedModel
from group_finance.apps.org.models import Company


class Person(TimeStampedModel, NoteMixin, ActiveMixin):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="persons",
        verbose_name="Пользователь",
        null=True,
        blank=True,
    )
    last_name = models.CharField("Фамилия", max_length=100)
    first_name = models.CharField("Имя", max_length=100)
    middle_name = models.CharField("Отчество", max_length=100, blank=True, default="")
    display_name = models.CharField(
        "Отображаемое имя", max_length=255, blank=True, default=""
    )
    email = models.EmailField("Email", blank=True)
    external_id = models.CharField(
        "Внешний ID",
        max_length=100,
        blank=True,
        default="",
        help_text="Идентификатор из внешней системы (например, Access)",
    )

    class Meta:
        verbose_name = "Человек"
        verbose_name_plural = "Люди"
        ordering = ("last_name", "first_name")
        constraints = [
            models.UniqueConstraint(
                fields=["external_id"],
                condition=Q(external_id__gt=""),
                name="uniq_person_external_id",
            ),
        ]

    def save(self, *args, **kwargs):
        if not self.display_name:
            parts = [self.last_name, self.first_name, self.middle_name]
            self.display_name = " ".join(p for p in parts if p).strip()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        if self.display_name:
            return self.display_name
        return f"{self.last_name} {self.first_name} {self.middle_name}".strip()


class PersonCompanyEngagement(TimeStampedModel, NoteMixin, ActiveMixin):
    class EngagementType(models.TextChoices):
        EMPLOYEE = "employee", "Сотрудник"
        CONTRACTOR = "contractor", "Подрядчик"
        FOUNDER = "founder", "Учредитель"

    person = models.ForeignKey(
        Person,
        on_delete=models.PROTECT,
        related_name="engagements",
        verbose_name="Человек",
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.PROTECT,
        related_name="person_engagements",
        verbose_name="Компания",
    )
    engagement_type = models.CharField(
        "Тип",
        max_length=20,
        choices=EngagementType.choices,
        default=EngagementType.EMPLOYEE,
    )
    job_title = models.CharField("Должность", max_length=255, blank=True, default="")
    start_date = models.DateField("Дата начала", null=True, blank=True)
    end_date = models.DateField("Дата окончания", null=True, blank=True)
    external_id = models.CharField(
        "Внешний ID",
        max_length=100,
        blank=True,
        default="",
        help_text="Идентификатор из внешней системы (например, Access)",
    )

    class Meta:
        verbose_name = "Занятость"
        verbose_name_plural = "Занятости"
        ordering = ("person__last_name", "person__first_name", "company__short_name")
        constraints = [
            models.UniqueConstraint(
                fields=["person", "company", "engagement_type"],
                name="uniq_engagement_person_company_type",
            ),
            models.UniqueConstraint(
                fields=["external_id"],
                condition=Q(external_id__gt=""),
                name="uniq_engagement_external_id",
            ),
        ]

    def clean(self):
        super().clean()
        if self.start_date and self.end_date and self.end_date < self.start_date:
            raise ValidationError(
                {"end_date": "Дата окончания не может быть раньше даты начала."}
            )

    def __str__(self) -> str:
        company_name = self.company.short_name or self.company.name
        return f"{self.person} @ {company_name} ({self.get_engagement_type_display()})"
