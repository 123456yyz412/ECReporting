from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("auth", "0012_alter_user_first_name_max_length"),
        ("datasources", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="UploadModule",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("table_name", models.CharField(max_length=255)),
                ("schema", models.CharField(blank=True, default="", max_length=255)),
                ("columns", models.JSONField(blank=True, default=dict)),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_upload_modules",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "datasource",
                    models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="upload_modules", to="datasources.datasourceinstance"),
                ),
                (
                    "groups",
                    models.ManyToManyField(blank=True, related_name="upload_modules", to="auth.group"),
                ),
            ],
        ),
        migrations.CreateModel(
            name="UploadJob",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("filename", models.CharField(max_length=255)),
                ("total_rows", models.IntegerField(default=0)),
                ("inserted_rows", models.IntegerField(default=0)),
                ("status", models.CharField(default="pending", max_length=20)),
                ("error", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="upload_jobs",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "module",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="jobs", to="datafill.uploadmodule"),
                ),
            ],
        ),
    ]

