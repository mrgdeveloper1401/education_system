# Generated by Django 5.1.2 on 2024-11-03 10:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Advertise",
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
                ("mobile_phone", models.CharField(verbose_name="شماره موبایل")),
                (
                    "subject_advertise",
                    models.CharField(
                        choices=[
                            ("how_to_signup", "چه جوری در کلاس ها ثبت نام کنم"),
                            ("course_start", "کدام دوره رو شروع کنم"),
                            ("installment", "درخواست خرید قسطی"),
                            ("what_happened", "در هر جلسه چه اتفاقی می افتد"),
                            ("buy_group", "درخواست خرید گروهی"),
                            ("other", "سایز"),
                        ],
                        max_length=13,
                        verbose_name="موضوع مشاوره",
                    ),
                ),
                (
                    "answered",
                    models.BooleanField(default=False, verbose_name="پاسخ داده شد"),
                ),
            ],
            options={
                "verbose_name": "مشاوره",
                "verbose_name_plural": "مشاوره ها",
                "db_table": "advertise",
            },
        ),
        migrations.CreateModel(
            name="DefineAdvertise",
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
                ("date", models.DateField(verbose_name="تاریخ مشاوره")),
                ("start_time", models.TimeField(verbose_name="ساعت شروع")),
                ("end_time", models.TimeField(verbose_name="ساعت پایان")),
                (
                    "is_available",
                    models.BooleanField(default=True, verbose_name="قابل رزرو"),
                ),
            ],
            options={
                "verbose_name": "بازه زمانی مشاوره",
                "verbose_name_plural": "بازه های زمانی مشاوره",
                "db_table": "define_advertise",
            },
        ),
        migrations.CreateModel(
            name="AnsweredAdvertise",
            fields=[],
            options={
                "verbose_name": "مشاوره پاسخ داده شده",
                "verbose_name_plural": "مشاوره های پاسخ داده شده",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("advertise.advertise",),
        ),
        migrations.AddField(
            model_name="advertise",
            name="slot",
            field=models.ForeignKey(
                limit_choices_to={"is_available": True},
                on_delete=django.db.models.deletion.PROTECT,
                related_name="advertise",
                to="advertise.defineadvertise",
                verbose_name="تاریخ مشاوره",
            ),
        ),
    ]
