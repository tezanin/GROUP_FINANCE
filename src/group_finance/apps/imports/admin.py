from django.contrib import admin

from .models import ImportBatch, ImportError, ImportFile, ImportRowRaw


@admin.register(ImportBatch)
class ImportBatchAdmin(admin.ModelAdmin):
    list_display = ("id", "import_type", "company", "status", "started_at", "finished_at")
    search_fields = ("import_type", "note", "company__name")
    list_filter = ("import_type", "status", "company")
    autocomplete_fields = ("company", "created_by")

    fieldsets = (
        ("Основное", {"fields": ("import_type", "company", "status", "created_by")}),
        ("Время", {"fields": ("started_at", "finished_at")}),
        ("Дополнительно", {"fields": ("note",)}),
    )


@admin.register(ImportFile)
class ImportFileAdmin(admin.ModelAdmin):
    list_display = ("id", "original_name", "batch", "status", "size_bytes", "created_at")
    search_fields = ("original_name", "mime_type", "note", "batch__import_type")
    list_filter = ("status", "mime_type", "created_at")
    autocomplete_fields = ("batch", "uploaded_by")

    fieldsets = (
        ("Основное", {"fields": ("batch", "file", "original_name", "status")}),
        ("Метаданные", {"fields": ("mime_type", "size_bytes", "uploaded_by")}),
        ("Дополнительно", {"fields": ("note",)}),
    )


@admin.register(ImportRowRaw)
class ImportRowRawAdmin(admin.ModelAdmin):
    list_display = ("id", "batch", "import_file", "row_number", "status", "created_at")
    search_fields = ("row_number", "batch__import_type", "import_file__original_name")
    list_filter = ("status", "batch__import_type", "created_at")
    autocomplete_fields = ("batch", "import_file")

    fieldsets = (
        ("Основное", {"fields": ("batch", "import_file", "row_number", "status")}),
        ("Данные", {"fields": ("raw_payload",)}),
    )


@admin.register(ImportError)
class ImportErrorAdmin(admin.ModelAdmin):
    list_display = ("id", "batch", "level", "error_code", "import_file", "created_at")
    search_fields = ("error_code", "message", "batch__import_type", "import_file__original_name")
    list_filter = ("level", "error_code", "created_at")
    autocomplete_fields = ("batch", "import_file", "import_row")

    fieldsets = (
        ("Основное", {"fields": ("batch", "import_file", "import_row", "level", "error_code")}),
        ("Сообщение", {"fields": ("message",)}),
    )