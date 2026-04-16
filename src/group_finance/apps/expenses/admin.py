from django.contrib import admin

from .models import Expense, ExpenseCategory


@admin.register(ExpenseCategory)
class ExpenseCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "code")
    search_fields = ("name", "code")

    fieldsets = (
        ("Основное", {
            "fields": (
                "name",
                "code",
            )
        }),
    )


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "category",
        "project",
        "business_direction",
        "period_start",
        "period_end",
        "amount",
        "currency",
        "recognized_date",
        "is_operational",
    )
    search_fields = (
        "company__name",
        "category__name",
        "category__code",
        "project__name",
        "business_direction__name",
        "note",
    )
    list_filter = (
        "company",
        "category",
        "currency",
        "is_operational",
        "recognized_date",
        "period_start",
    )
    autocomplete_fields = (
        "company",
        "category",
        "project",
        "business_direction",
        "currency",
    )

    fieldsets = (
        ("Основное", {
            "fields": (
                "company",
                "category",
                "amount",
                "currency",
                "is_operational",
            )
        }),
        ("Аналитика", {
            "fields": (
                "project",
                "business_direction",
            )
        }),
        ("Период", {
            "fields": (
                "period_start",
                "period_end",
                "recognized_date",
            )
        }),
        ("Дополнительно", {
            "fields": ("note",)
        }),
    )