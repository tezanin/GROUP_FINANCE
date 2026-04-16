from django.contrib import admin

from .models import BankTransaction


@admin.register(BankTransaction)
class BankTransactionAdmin(admin.ModelAdmin):
    list_display = ("company", "bank_account", "transaction_date", "direction", "amount", "currency")
    search_fields = ("company__name", "bank_account__account_number", "description", "external_id", "note")
    list_filter = ("company", "currency", "direction", "transaction_date")
    autocomplete_fields = ("company", "bank_account", "currency")

    fieldsets = (
        ("Основное", {"fields": ("company", "bank_account", "transaction_date", "direction", "amount", "currency")}),
        ("Описание", {"fields": ("description", "external_id")}),
        ("Дополнительно", {"fields": ("note",)}),
    )