from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Branding",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("company_name", models.CharField(default="ECReporting", max_length=200)),
                ("logo", models.ImageField(blank=True, null=True, upload_to="branding/")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
    ]

