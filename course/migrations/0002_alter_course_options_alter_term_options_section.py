# Generated by Django 5.1.2 on 2024-12-13 07:56

import course.models
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("course", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="course",
            options={"verbose_name": "درس", "verbose_name_plural": "درس ها"},
        ),
        migrations.AlterModelOptions(
            name="term",
            options={"verbose_name": "ترم", "verbose_name_plural": "ترم ها"},
        ),
        migrations.CreateModel(
            name="Section",
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
                    "video",
                    models.FileField(
                        upload_to=course.models.course_name,
                        validators=[
                            django.core.validators.FileExtensionValidator("mp4")
                        ],
                    ),
                ),
                ("video_title", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "course",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="sections",
                        to="course.course",
                    ),
                ),
            ],
            options={
                "verbose_name": "قسمت",
                "verbose_name_plural": "قسمت های دوره",
                "db_table": "course_section",
                "ordering": ("created_at",),
            },
        ),
    ]
