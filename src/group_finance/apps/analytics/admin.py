from django.contrib import admin

from .models import ReportSnapshot


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
