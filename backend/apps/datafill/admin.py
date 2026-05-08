from django.contrib import admin

from .models import UploadJob, UploadModule


@admin.register(UploadModule)
class UploadModuleAdmin(admin.ModelAdmin):
    list_display = ("name", "datasource", "table_name", "schema", "is_active", "created_by", "created_at")
    search_fields = ("name", "table_name")


@admin.register(UploadJob)
class UploadJobAdmin(admin.ModelAdmin):
    list_display = ("module", "filename", "status", "total_rows", "inserted_rows", "created_by", "created_at")
    search_fields = ("filename",)
