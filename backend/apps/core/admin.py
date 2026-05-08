from django.contrib import admin

from .models import Branding, CustomBackground


@admin.register(Branding)
class BrandingAdmin(admin.ModelAdmin):
    list_display = ("company_name", "updated_at")


@admin.register(CustomBackground)
class CustomBackgroundAdmin(admin.ModelAdmin):
    list_display = ("name", "created_by", "created_at")
