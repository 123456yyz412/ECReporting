from django.contrib import admin

from .models import Collection, Dashboard, Query


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_by", "created_at")
    search_fields = ("name",)


@admin.register(Query)
class QueryAdmin(admin.ModelAdmin):
    list_display = ("name", "collection", "datasource", "is_hidden", "created_by", "created_at")
    search_fields = ("name",)


@admin.register(Dashboard)
class DashboardAdmin(admin.ModelAdmin):
    list_display = ("name", "collection", "layout_mode", "created_by", "created_at")
    search_fields = ("name",)
