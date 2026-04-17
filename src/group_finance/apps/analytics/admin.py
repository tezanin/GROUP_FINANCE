from django.contrib import admin

from .models import Adjustment, Allocation, ReconciliationRecord, ReportSnapshot


@admin.register(ReportSnapshot)
class ReportSnapshotAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "project",
        "report_type",
        "period_start",
        "period_end",
        "generated_at",
    )
    search_fields = (
        "company__name",
        "project__name",
        "report_type",
    )
    list_filter = (
        "company",
        "report_type",
        "period_start",
        "generated_at",
    )
    autocomplete_fields = ("company", "project")


@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "source_type",
        "source_id",
        "allocation_date",
        "amount",
        "currency",
        "project",
        "business_direction",
        "expense_category",
    )
    search_fields = (
        "company__name",
        "source_type",
        "source_id",
    )
    list_filter = (
        "company",
        "source_type",
        "currency",
        "allocation_date",
    )
    autocomplete_fields = (
        "company",
        "currency",
        "project",
        "business_direction",
        "expense_category",
    )

    fieldsets = (
        ("Источник", {
            "fields": (
                "company",
                "source_type",
                "source_id",
                "allocation_date",
            )
        }),
        ("Сумма", {
            "fields": (
                "amount",
                "currency",
            )
        }),
        ("Аналитика", {
            "fields": (
                "project",
                "business_direction",
                "expense_category",
            )
        }),
    )


@admin.register(Adjustment)
class AdjustmentAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "target_type",
        "target_id",
        "adjustment_date",
        "amount",
        "currency",
    )
    search_fields = (
        "company__name",
        "target_type",
        "target_id",
        "reason",
    )
    list_filter = (
        "company",
        "target_type",
        "currency",
        "adjustment_date",
    )
    autocomplete_fields = ("company", "currency")

    fieldsets = (
        ("Объект", {
            "fields": (
                "company",
                "target_type",
                "target_id",
                "adjustment_date",
            )
        }),
        ("Сумма", {
            "fields": (
                "amount",
                "currency",
            )
        }),
        ("Причина", {
            "fields": ("reason",)
        }),
    )


@admin.register(ReconciliationRecord)
class ReconciliationRecordAdmin(admin.ModelAdmin):
    list_display = (
        "company",
        "left_source_type",
        "left_source_id",
        "right_source_type",
        "right_source_id",
        "status",
        "difference_amount",
        "currency",
        "checked_at",
    )
    search_fields = (
        "company__name",
        "left_source_type",
        "left_source_id",
        "right_source_type",
        "right_source_id",
    )
    list_filter = (
        "company",
        "status",
        "currency",
        "checked_at",
    )
    autocomplete_fields = ("company", "currency")

    fieldsets = (
        ("Левый источник", {
            "fields": (
                "company",
                "left_source_type",
                "left_source_id",
            )
        }),
        ("Правый источник", {
            "fields": (
                "right_source_type",
                "right_source_id",
            )
        }),
        ("Результат", {
            "fields": (
                "status",
                "difference_amount",
                "currency",
                "checked_at",
            )
        }),
    )