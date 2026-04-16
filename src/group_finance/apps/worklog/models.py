from django.core.exceptions import ValidationError
from django.db import models

from group_finance.apps.core.models import TimeStampedModel
from group_finance.apps.org.models import Company, Project
from group_finance.apps.people.models import Employee


class TimesheetEntry(TimeStampedModel):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name="timesheet_entries", verbose_name="Сотрудник")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="timesheet_entries", verbose_name="Компания")
    project = models.ForeignKey(Project, on_delete=models.PROTECT, related_name="timesheet_entries", verbose_name="Проект")
    work_date = models.DateField("Дата работы")
    hours = models.DecimalField("Часы", max_digits=6, decimal_places=2)
    description = models.TextField("Описание", blank=True)
    is_billable = models.BooleanField("Биллабельно", default=True)

    class Meta:
        verbose_name = "Запись таймшита"
        verbose_name_plural = "Записи таймшита"
        ordering = ("-work_date", "-id")

    def clean(self):
        super().clean()
        errors = {}
        if self.hours is not None and self.hours <= 0:
            errors["hours"] = "Количество часов должно быть больше нуля."
        if self.employee_id and self.company_id and self.employee.company_id != self.company_id:
            errors["employee"] = "Сотрудник должен относиться к выбранной компании."
        if self.project_id and self.company_id and self.project.company_id != self.company_id:
            errors["project"] = "Проект должен относиться к выбранной компании."
        if errors:
            raise ValidationError(errors)

    def __str__(self) -> str:
        return f"{self.employee} | {self.work_date} | {self.hours}"