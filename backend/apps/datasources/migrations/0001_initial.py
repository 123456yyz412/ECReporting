from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DataSourceInstance",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("db_type", models.CharField(choices=[("postgres", "PostgreSQL"), ("mysql", "MySQL")], max_length=20)),
                ("host", models.CharField(max_length=255)),
                ("port", models.IntegerField()),
                ("database", models.CharField(max_length=255)),
                ("schema", models.CharField(blank=True, default="", max_length=255)),
                ("username", models.CharField(max_length=255)),
                ("password", models.TextField()),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="created_datasources",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
