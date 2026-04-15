from django.conf import settings
from django.db import models

from group_finance.apps.core.models import ActiveMixin, NoteMixin, TimeStampedModel
from group_finance.apps.org.models import Company


class Employee(TimeStampedModel, NoteMixin, ActiveMixin):
    class EmploymentType(models.TextChoices):
        EMPLOYEE = "employee", "Сотрудник"
        CONTRACTOR = "contractor", "Подрядчик"
        FOUNDER = "founder", "Учредитель"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name="employees",
        verbose_name="Пользователь",
        null=True,
        blank=True,
    )

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="employees",
        verbose_name="Компания",
    )

    full_name = models.CharField("ФИО", max_length=255)
    email = models.EmailField("Email", blank=True)

    employment_type = models.CharField(
        "Тип",
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.EMPLOYEE,
    )

    position = models.CharField("Должность", max_length=255, blank=True)

    hire_date = models.DateField("Дата найма", null=True, blank=True)
    fire_date = models.DateField("Дата увольнения", null=True, blank=True)

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ("full_name",)

    def __str__(self) -> str:
        return self.full_name
