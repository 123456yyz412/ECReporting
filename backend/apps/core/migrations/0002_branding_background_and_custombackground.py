from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="branding",
            name="page_background_kind",
            field=models.CharField(default="builtin", max_length=20),
        ),
        migrations.AddField(
            model_name="branding",
            name="page_background_value",
            field=models.CharField(default="cross-border-ocean", max_length=100),
        ),
        migrations.CreateModel(
            name="CustomBackground",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200)),
                ("image", models.ImageField(upload_to="backgrounds/")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="custom_backgrounds",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
