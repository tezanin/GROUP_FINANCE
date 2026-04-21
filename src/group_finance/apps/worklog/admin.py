from django.contrib import admin

from .models import TimesheetEntry


@admin.register(TimesheetEntry)
class TimesheetEntryAdmin(admin.ModelAdmin):
    list_display = ("engagement", "company", "project", "work_date", "hours", "is_billable")
    search_fields = ("engagement__person__last_name", "engagement__person__first_name", "engagement__person__email", "company__name", "project__name", "description")
    list_filter = ("company", "project", "is_billable", "work_date")
    autocomplete_fields = ("engagement", "company", "project")

    fieldsets = (
        ("Основное", {"fields": ("engagement", "company", "project", "work_date", "hours", "is_billable")}),
        ("Описание", {"fields": ("description",)}),
    )
