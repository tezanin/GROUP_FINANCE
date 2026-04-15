from django.contrib import admin

from .models import (
    Attachment,
    AuditLog,
    Comment,
    Currency,
    ExchangeRate,
    ExchangeRateSource,
)


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active", "created_at")
    search_fields = ("code", "name")
    list_filter = ("is_active",)


@admin.register(ExchangeRateSource)
class ExchangeRateSourceAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_manual", "created_at")
    search_fields = ("code", "name")
    list_filter = ("is_manual",)


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
    search_fields = ("currency__code", "source__name")
    list_filter = ("source", "is_manual_override", "rate_date")
    autocomplete_fields = ("currency", "source")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "created_by", "is_active", "created_at")
    search_fields = ("content", "note", "created_by__username")
    list_filter = ("is_active", "created_at")
    autocomplete_fields = ("created_by",)


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ("id", "original_name", "uploaded_by", "size_bytes", "is_active", "created_at")
    search_fields = ("original_name", "mime_type", "note", "uploaded_by__username")
    list_filter = ("is_active", "mime_type", "created_at")
    autocomplete_fields = ("uploaded_by",)


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("id", "entity_type", "entity_id", "action", "actor", "created_at")
    search_fields = ("entity_type", "entity_id", "action")
    list_filter = ("action", "entity_type", "created_at")
    autocomplete_fields = ("actor",)