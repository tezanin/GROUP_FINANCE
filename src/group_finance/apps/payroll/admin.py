
from django.contrib import admin

from .models import Payroll, SalaryRate


@admin.register(SalaryRate)
class SalaryRateAdmin(admin.ModelAdmin):
    list_display = ("employee", "amount", "currency", "effective_from")
    search_fields = ("employee__full_name",)
    list_filter = ("currency",)
    autocomplete_fields = ("employee", "currency")


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ("employee", "period_start", "period_end", "amount", "currency", "is_paid")
    search_fields = ("employee__full_name",)
    list_filter = ("currency", "is_paid", "period_start")
    autocomplete_fields = ("employee", "currency")