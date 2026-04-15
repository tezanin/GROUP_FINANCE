from django.contrib import admin

from .models import Employee


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("full_name", "company", "employment_type", "position", "is_active")
    search_fields = ("full_name", "email", "position")
    list_filter = ("company", "employment_type", "is_active")
    autocomplete_fields = ("company", "user")
