from django.contrib import admin

from .models import Person, PersonCompanyEngagement


# ---------------------
# Person
# ---------------------
@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = (
        "display_name_or_fallback",
        "last_name",
        "first_name",
        "email",
        "is_active",
    )
    search_fields = (
        "last_name",
        "first_name",
        "middle_name",
        "display_name",
        "email",
        "external_id",
    )
    list_filter = ("is_active",)
    autocomplete_fields = ("user",)
    ordering = ("last_name", "first_name")

    fieldsets = (
        ("Основное", {
            "fields": (
                "last_name",
                "first_name",
                "middle_name",
                "display_name",
            )
        }),
        ("Контакты", {
            "fields": ("email",)
        }),
        ("Дополнительно", {
            "fields": (
                "user",
                "external_id",
                "is_active",
                "note",
            )
        }),
    )

    @admin.display(description="Имя")
    def display_name_or_fallback(self, obj):
        return str(obj)


# ---------------------
# PersonCompanyEngagement
# ---------------------
@admin.register(PersonCompanyEngagement)
class PersonCompanyEngagementAdmin(admin.ModelAdmin):
    list_display = (
        "person",
        "company",
        "engagement_type",
        "job_title",
        "start_date",
        "end_date",
        "is_active",
    )
    list_filter = ("company", "engagement_type", "is_active")
    search_fields = (
        "person__last_name",
        "person__first_name",
        "job_title",
        "external_id",
    )
    autocomplete_fields = ("person", "company")
    ordering = ("person__last_name", "person__first_name")

    fieldsets = (
        ("Основное", {
            "fields": (
                "person",
                "company",
                "engagement_type",
                "job_title",
            )
        }),
        ("Период", {
            "fields": (
                "start_date",
                "end_date",
            )
        }),
        ("Дополнительно", {
            "fields": (
                "external_id",
                "is_active",
                "note",
            )
        }),
    )
