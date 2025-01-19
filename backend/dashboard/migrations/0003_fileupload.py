# Generated by Django 5.1.5 on 2025-01-18 21:15

import dashboard.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dashboard", "0002_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="FileUpload",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("file", models.FileField(upload_to=dashboard.models.csv_upload_path)),
                ("uploaded_at", models.DateTimeField(auto_now_add=True)),
                (
                    "dashboard",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="files",
                        to="dashboard.dashboard",
                    ),
                ),
            ],
        ),
    ]
