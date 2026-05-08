from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models

from apps.datasources.models import DataSourceInstance


class UploadModule(models.Model):
    name = models.CharField(max_length=200)
    datasource = models.ForeignKey(DataSourceInstance, on_delete=models.PROTECT, related_name="upload_modules")
    table_name = models.CharField(max_length=255)
    schema = models.CharField(max_length=255, blank=True, default="")
    columns = models.JSONField(default=dict, blank=True)
    groups = models.ManyToManyField(Group, blank=True, related_name="upload_modules")
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_upload_modules"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Upload Module"
        verbose_name_plural = "Upload Modules"

    def __str__(self) -> str:
        return self.name


class UploadJob(models.Model):
    module = models.ForeignKey(UploadModule, on_delete=models.CASCADE, related_name="jobs")
    filename = models.CharField(max_length=255)
    total_rows = models.IntegerField(default=0)
    inserted_rows = models.IntegerField(default=0)
    status = models.CharField(max_length=20, default="pending")
    error = models.TextField(blank=True, default="")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="upload_jobs"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Upload Job"
        verbose_name_plural = "Upload Jobs"
