from django.contrib import admin

from .models import Revenue


@admin.register(Revenue)
class RevenueAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "client",
        "project",
        "period_start",
        "period_end",
        "amount",
        "currency",
        "recognized_date",
    )
    search_fields = (
        "company__name",
        "client__name",
        "project__name",
        "note",
    )
    list_filter = (
        "company",
        "client",
        "currency",
        "recognized_date",
        "period_start",
    )
    autocomplete_fields = ("company", "client", "project", "currency")
