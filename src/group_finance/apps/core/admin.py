from django.contrib import admin

from group_finance.apps.core.models import Currency, ExchangeRate, ExchangeRateSource


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "created_at", "updated_at")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
    ordering = ("code",)


@admin.register(ExchangeRateSource)
class ExchangeRateSourceAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_manual", "created_at", "updated_at")
    list_filter = ("is_manual",)
    search_fields = ("code", "name", "note")
    ordering = ("name", "code")


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = (
        "currency",
        "rate_date",
        "rate_to_rub",
        "source",
        "is_manual_override",
        "created_at",
    )
    list_filter = ("rate_date", "source", "is_manual_override")
    search_fields = (
        "currency__code",
        "currency__name",
        "source__code",
        "source__name",
        "note",
    )
    autocomplete_fields = ("currency", "source")
    date_hierarchy = "rate_date"
    ordering = ("-rate_date", "currency__code", "source__name")
