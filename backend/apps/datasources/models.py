from django.conf import settings
from django.db import models


class DataSourceType(models.TextChoices):
    POSTGRES = "postgres", "PostgreSQL"
    MYSQL = "mysql", "MySQL"


class DataSourceInstance(models.Model):
    name = models.CharField(max_length=200)
    db_type = models.CharField(max_length=20, choices=DataSourceType.choices)
    host = models.CharField(max_length=255)
    port = models.IntegerField()
    database = models.CharField(max_length=255)
    schema = models.CharField(max_length=255, blank=True, default="")
    username = models.CharField(max_length=255)
    password = models.TextField()
    is_active = models.BooleanField(default=True)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="created_datasources"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Data Source Instance"
        verbose_name_plural = "Data Source Instances"

    def __str__(self) -> str:
        return f"{self.name} ({self.db_type})"
