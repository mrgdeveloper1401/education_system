# Generated by Django 5.1.2 on 2024-11-07 19:51

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="SiteSettings",
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
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "deleted_at",
                    models.DateTimeField(blank=True, editable=False, null=True),
                ),
                ("is_deleted", models.BooleanField(default=False, editable=False)),
                (
                    "site_logo",
                    models.ImageField(upload_to="", verbose_name="عکس لوگوی سایت"),
                ),
                ("location", django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
            options={
                "abstract": False,
            },
        ),
    ]
