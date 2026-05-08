from django.conf import settings
from django.contrib.auth.models import Group
from django.db import models

from apps.datasources.models import DataSourceInstance


class Collection(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, default="")
    groups = models.ManyToManyField(Group, blank=True, related_name="report_collections")
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_collections"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Report Collection"
        verbose_name_plural = "Report Collections"

    def __str__(self) -> str:
        return self.name


class Query(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name="queries")
    datasource = models.ForeignKey(DataSourceInstance, on_delete=models.PROTECT, related_name="queries")
    name = models.CharField(max_length=200)
    sql_text = models.TextField()
    is_hidden = models.BooleanField(default=False)

    visualization_type = models.CharField(max_length=50, default="table")
    visualization_config = models.JSONField(default=dict, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_queries"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Query"
        verbose_name_plural = "Queries"

    def __str__(self) -> str:
        return self.name


class Dashboard(models.Model):
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name="dashboards")
    name = models.CharField(max_length=200)
    layout_mode = models.CharField(max_length=20, default="screen")
    background = models.JSONField(default=dict, blank=True)
    definition = models.JSONField(default=dict, blank=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_dashboards"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Dashboard"
        verbose_name_plural = "Dashboards"

    def __str__(self) -> str:
        return self.name
