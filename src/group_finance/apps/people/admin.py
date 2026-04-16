from django.contrib import admin

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "company",
        "employment_type",
        "position",
        "email",
        "is_active",
    )
    search_fields = ("full_name", "email", "position", "company__name")
    list_filter = ("company", "employment_type", "is_active")
    autocomplete_fields = ("company", "user")

    fieldsets = (
        ("Основное", {
            "fields": (
                "full_name",
                "company",
                "user",
                "employment_type",
                "position",
            )
        }),
        ("Контакты", {
            "fields": ("email",)
        }),
        ("Даты", {
            "fields": (
                "hire_date",
                "fire_date",
            )
        }),
        ("Дополнительно", {
            "fields": (
                "is_active",
                "note",
            )
        }),
    )