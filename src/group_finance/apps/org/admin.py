from django.contrib import admin

from .models import BankAccount, BusinessDirection, Client, Company, Project


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "short_name",
        "company_type",
        "registration_country",
        "base_currency",
        "is_active",
    )
    search_fields = ("name", "short_name", "tax_id")
    list_filter = ("company_type", "registration_country", "is_active")
    autocomplete_fields = ("base_currency",)

    fieldsets = (
        ("Основное", {
            "fields": (
                "name",
                "short_name",
                "company_type",
                "registration_country",
                "base_currency",
            )
        }),
        ("Реквизиты", {
            "fields": (
                "tax_id",
            )
        }),
        ("Дополнительно", {
            "fields": (
                "is_active",
                "note",
            )
        }),
    )


@admin.register(BusinessDirection)
class BusinessDirectionAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "company", "is_active")
    search_fields = ("name", "code", "company__name")
    list_filter = ("company", "is_active")
    autocomplete_fields = ("company",)

    fieldsets = (
        ("Основное", {
            "fields": (
                "name",
                "code",
                "company",
            )
        }),
        ("Дополнительно", {
            "fields": (
                "is_active",
                "note",
            )
        }),
    )


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "tax_id", "is_active")
    search_fields = ("name", "tax_id", "company__name")
    list_filter = ("company", "is_active")
    autocomplete_fields = ("company",)

    fieldsets = (
        ("Основное", {
            "fields": (
                "name",
                "company",
                "tax_id",
            )
        }),
        ("Дополнительно", {
            "fields": (
                "is_active",
                "note",
            )
        }),
    )


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "company", "business_direction", "client", "is_active")
    search_fields = ("name", "code", "company__name", "client__name")
    list_filter = ("company", "business_direction", "is_active")
    autocomplete_fields = ("company", "business_direction", "client")

    prepopulated_fields = {"code": ("name",)}

    fieldsets = (
        ("Основное", {
            "fields": (
                "name",
                "code",
                "company",
                "business_direction",
                "client",
            )
        }),
        ("Дополнительно", {
            "fields": (
                "is_active",
                "note",
            )
        }),
    )


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = ("company", "bank_name", "account_number", "currency", "is_primary", "is_active")
    search_fields = ("company__name", "bank_name", "account_number")
    list_filter = ("company", "currency", "is_primary", "is_active")
    autocomplete_fields = ("company", "currency")

    fieldsets = (
        ("Основное", {
            "fields": (
                "company",
                "bank_name",
                "account_number",
                "currency",
            )
        }),
        ("Признаки", {
            "fields": (
                "is_primary",
                "is_active",
            )
        }),
        ("Дополнительно", {
            "fields": (
                "note",
            )
        }),
    )