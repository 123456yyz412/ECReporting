from django.contrib import admin

from .models import DataSourceInstance


@admin.register(DataSourceInstance)
class DataSourceInstanceAdmin(admin.ModelAdmin):
    list_display = ("name", "db_type", "host", "port", "database", "schema", "is_active", "created_at")
    search_fields = ("name", "host", "database")
