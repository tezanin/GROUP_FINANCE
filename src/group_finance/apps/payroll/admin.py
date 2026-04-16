from django.contrib import admin

from .models import Payroll, SalaryRate


@admin.register(SalaryRate)
class SalaryRateAdmin(admin.ModelAdmin):
    list_display = ("employee", "amount", "currency", "effective_from", "created_at")
    search_fields = ("employee__full_name", "employee__email")
    list_filter = ("currency", "effective_from", "created_at")
    autocomplete_fields = ("employee", "currency")

    fieldsets = (
        ("Основное", {
            "fields": (
                "employee",
                "amount",
                "currency",
                "effective_from",
            )
        }),
    )


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = (
        "employee",
        "period_start",
        "period_end",
        "amount",
        "currency",
        "is_paid",
    )
    search_fields = ("employee__full_name", "employee__email")
    list_filter = ("currency", "is_paid", "period_start", "period_end")
    autocomplete_fields = ("employee", "currency")

    fieldsets = (
        ("Основное", {
            "fields": (
                "employee",
                "amount",
                "currency",
            )
        }),
        ("Период", {
            "fields": (
                "period_start",
                "period_end",
            )
        }),
        ("Статус", {
            "fields": ("is_paid",)
        }),
    )