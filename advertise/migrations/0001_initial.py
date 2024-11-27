# Generated by Django 5.1.2 on 2024-11-27 22:09

import accounts.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ConsultationSchedule",
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
                ("start_date", models.DateField()),
                ("end_date", models.DateField()),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("interval", models.PositiveSmallIntegerField(default=2)),
            ],
            options={
                "db_table": "consultation_schedule",
            },
        ),
        migrations.CreateModel(
            name="ConsultationTopic",
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
                ("name", models.CharField(max_length=255, unique=True)),
            ],
            options={
                "db_table": "consultation_topic",
            },
        ),
        migrations.CreateModel(
            name="ConsultationSlot",
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
                ("date", models.DateField()),
                ("start_time", models.TimeField()),
                ("end_time", models.TimeField()),
                ("is_available", models.BooleanField(default=True)),
                (
                    "schedule",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="consultation_slot",
                        to="advertise.consultationschedule",
                    ),
                ),
            ],
            options={
                "db_table": "consultation_slot",
            },
        ),
        migrations.CreateModel(
            name="ConsultationRequest",
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
                (
                    "mobile_phone",
                    models.CharField(
                        max_length=11,
                        validators=[accounts.validators.MobileRegexValidator()],
                        verbose_name="شماره موبایل",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(max_length=30, verbose_name="نام کد اموز"),
                ),
                (
                    "last_name",
                    models.CharField(
                        max_length=30, verbose_name="نام خانوادگی کد اموز"
                    ),
                ),
                (
                    "classroom",
                    models.CharField(
                        choices=[
                            ("one", "اول"),
                            ("two", "دوم"),
                            ("three", "سوم"),
                            ("four", "چهارم"),
                            ("five", "پنجم"),
                            ("six", "ششم"),
                            ("seven", "هفتم"),
                            ("eight", "هشتم"),
                            ("nine", "نهم"),
                            ("ten", "دهم"),
                            ("eleven", "یازدهم"),
                            ("twelfth", "دوازدهم"),
                            ("graduate", "فارغ التحصیل"),
                        ],
                        max_length=8,
                        verbose_name="پایه درسی",
                    ),
                ),
                (
                    "gender",
                    models.CharField(
                        choices=[("male", "male"), ("female", "female")],
                        max_length=6,
                        verbose_name="جنسیت",
                    ),
                ),
                ("is_answer", models.BooleanField(default=False)),
                (
                    "slot",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="consultation_slot_slot",
                        to="advertise.consultationslot",
                    ),
                ),
                (
                    "topic",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="consultation_request_topic",
                        to="advertise.consultationtopic",
                    ),
                ),
            ],
            options={
                "db_table": "consultation_request",
            },
        ),
    ]
