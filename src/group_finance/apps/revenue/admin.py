from django.contrib import admin

from .models import Act, ActLine, Invoice, InvoiceLine, Revenue


@admin.register(Revenue)
class RevenueAdmin(admin.ModelAdmin):
    list_display = ("company", "client", "project", "period_start", "period_end", "amount", "currency", "recognized_date")
    search_fields = ("company__name", "client__name", "project__name", "note")
    list_filter = ("company", "client", "currency", "recognized_date", "period_start")
    autocomplete_fields = ("company", "client", "project", "currency")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ("number", "company", "client", "project", "issue_date", "due_date", "total_amount", "currency", "status")
    search_fields = ("number", "company__name", "client__name", "project__name", "note")
    list_filter = ("company", "client", "currency", "status", "issue_date")
    autocomplete_fields = ("company", "client", "project", "currency")

    fieldsets = (
        ("Основное", {"fields": ("number", "company", "client", "project")}),
        ("Даты и статус", {"fields": ("issue_date", "due_date", "status")}),
        ("Сумма", {"fields": ("total_amount", "currency")}),
        ("Дополнительно", {"fields": ("note",)}),
    )


@admin.register(InvoiceLine)
class InvoiceLineAdmin(admin.ModelAdmin):
    list_display = ("invoice", "line_number", "quantity", "unit_price", "created_at")
    search_fields = ("invoice__number", "description")
    list_filter = ("invoice__company", "created_at")
    autocomplete_fields = ("invoice",)

    fieldsets = (
        ("Основное", {"fields": ("invoice", "line_number", "description", "quantity", "unit_price")}),
    )


@admin.register(Act)
class ActAdmin(admin.ModelAdmin):
    list_display = ("number", "company", "client", "project", "act_date", "total_amount", "currency", "status")
    search_fields = ("number", "company__name", "client__name", "project__name", "note")
    list_filter = ("company", "client", "currency", "status", "act_date")
    autocomplete_fields = ("company", "client", "project", "currency")

    fieldsets = (
        ("Основное", {"fields": ("number", "company", "client", "project")}),
        ("Дата и статус", {"fields": ("act_date", "status")}),
        ("Сумма", {"fields": ("total_amount", "currency")}),
        ("Дополнительно", {"fields": ("note",)}),
    )


@admin.register(ActLine)
class ActLineAdmin(admin.ModelAdmin):
    list_display = ("act", "line_number", "quantity", "unit_price", "created_at")
    search_fields = ("act__number", "description")
    list_filter = ("act__company", "created_at")
    autocomplete_fields = ("act",)

    fieldsets = (
        ("Основное", {"fields": ("act", "line_number", "description", "quantity", "unit_price")}),
    )