from django.contrib import admin

from .models import TimesheetEntry


@admin.register(TimesheetEntry)
class TimesheetEntryAdmin(admin.ModelAdmin):
    list_display = ("employee", "company", "project", "work_date", "hours", "is_billable")
    search_fields = ("employee__full_name", "employee__email", "company__name", "project__name", "description")
    list_filter = ("company", "project", "is_billable", "work_date")
    autocomplete_fields = ("employee", "company", "project")

    fieldsets = (
        ("Основное", {"fields": ("employee", "company", "project", "work_date", "hours", "is_billable")}),
        ("Описание", {"fields": ("description",)}),
    )