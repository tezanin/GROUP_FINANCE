from django.contrib import admin

from .models import Payroll, PayrollPayment, SalaryRate


@admin.register(SalaryRate)
class SalaryRateAdmin(admin.ModelAdmin):
    list_display = ("engagement", "amount", "currency", "effective_from", "created_at")
    search_fields = ("engagement__person__last_name", "engagement__person__first_name", "engagement__person__email")
    list_filter = ("currency", "effective_from", "created_at")
    autocomplete_fields = ("engagement", "currency")

    fieldsets = (
        ("Основное", {"fields": ("engagement", "amount", "currency", "effective_from")}),
    )


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ("engagement", "period_start", "period_end", "amount", "currency", "is_paid")
    search_fields = ("engagement__person__last_name", "engagement__person__first_name", "engagement__person__email")
    list_filter = ("currency", "is_paid", "period_start", "period_end")
    autocomplete_fields = ("engagement", "currency")

    fieldsets = (
        ("Основное", {"fields": ("engagement", "amount", "currency")}),
        ("Период", {"fields": ("period_start", "period_end")}),
        ("Статус", {"fields": ("is_paid",)}),
    )


@admin.register(PayrollPayment)
class PayrollPaymentAdmin(admin.ModelAdmin):
    list_display = ("engagement", "company", "payroll", "payment_date", "amount", "currency", "status")
    search_fields = ("engagement__person__last_name", "engagement__person__first_name", "engagement__person__email", "company__name", "note")
    list_filter = ("company", "currency", "status", "payment_date")
    autocomplete_fields = ("company", "engagement", "payroll", "currency")

    fieldsets = (
        ("Основное", {"fields": ("company", "engagement", "payroll", "payment_date", "amount", "currency", "status")}),
        ("Дополнительно", {"fields": ("note",)}),
    )
