# Generated by Django 5.1.2 on 2024-11-17 15:34

import images.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Image",
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
                (
                    "is_deleted",
                    models.BooleanField(default=False, editable=False, null=True),
                ),
                ("title", models.CharField(blank=True, max_length=128, null=True)),
                (
                    "image",
                    models.ImageField(
                        height_field="height",
                        help_text="max size is 5 MG",
                        upload_to="images/%Y/%m/%d",
                        validators=[images.validators.validate_image_size],
                        width_field="width",
                    ),
                ),
                ("width", models.IntegerField(blank=True, null=True)),
                ("height", models.IntegerField(blank=True, null=True)),
                ("file_hash", models.CharField(blank=True, max_length=40, null=True)),
                (
                    "file_size",
                    models.PositiveIntegerField(
                        blank=True, help_text="file size as xx.b", null=True
                    ),
                ),
                ("focal_point_x", models.PositiveIntegerField(blank=True, null=True)),
                ("focal_point_y", models.PositiveIntegerField(blank=True, null=True)),
                (
                    "focal_point_width",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "focal_point_height",
                    models.PositiveIntegerField(blank=True, null=True),
                ),
                (
                    "image_base64",
                    models.TextField(
                        blank=True, null=True, verbose_name="تبدیل به فورمت base64"
                    ),
                ),
            ],
            options={
                "verbose_name": "Image",
                "verbose_name_plural": "Images",
                "db_table": "image",
            },
        ),
    ]
