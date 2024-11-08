# Generated by Django 5.1.2 on 2024-11-08 13:28

import accounts.validators
import django.contrib.gis.db.models.fields
import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("images", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="FooterLogo",
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
                    "logo",
                    models.ImageField(
                        upload_to="main_settings/footer_logo",
                        verbose_name="عکس های فوتر",
                    ),
                ),
                ("logo_url", models.URLField(verbose_name="ادرس لوگو")),
                (
                    "is_publish",
                    models.BooleanField(default=True, verbose_name="انشتار در سایت"),
                ),
            ],
            options={
                "verbose_name": "عکس فوتر",
                "verbose_name_plural": "عکس های فوتر",
                "db_table": "footer_logo",
            },
        ),
        migrations.CreateModel(
            name="FooterSocial",
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
                    "social_image",
                    models.ImageField(
                        upload_to="main_settings/footer_social",
                        verbose_name="عکس شبکه اجتماعی",
                    ),
                ),
                ("social_url", models.URLField(verbose_name="ادرس شبکه اجتماعی")),
                (
                    "is_publish",
                    models.BooleanField(default=True, verbose_name="قابلیت انتشار"),
                ),
            ],
            options={
                "verbose_name": "شبکه اجتماعی",
                "verbose_name_plural": "شبکه های اجتماعی",
                "db_table": "footer_social",
            },
        ),
        migrations.CreateModel(
            name="FrequencyAskQuestion",
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
                    "question",
                    models.CharField(max_length=255, verbose_name="عنوان سوال"),
                ),
                (
                    "explain_question",
                    models.TextField(verbose_name="توضیح در مورد سوال"),
                ),
            ],
            options={
                "verbose_name": "سوالات متداول",
                "verbose_name_plural": "سوالات متداول",
                "db_table": "frequency_ask_question",
            },
        ),
        migrations.CreateModel(
            name="HeaderSite",
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
                    "header_title",
                    models.CharField(max_length=20, verbose_name="نام هدر"),
                ),
                ("link", models.URLField(verbose_name="ادرس")),
            ],
            options={
                "verbose_name": "هدر سایت",
                "verbose_name_plural": "هدر سایت",
                "db_table": "header_site",
            },
        ),
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
                    models.ImageField(
                        upload_to="main_settings/site_logo",
                        verbose_name="عکس لوگوی سایت",
                    ),
                ),
                (
                    "header_image",
                    models.ImageField(
                        upload_to="main_settings/header_image",
                        verbose_name="عکس هدر سایت",
                    ),
                ),
                (
                    "header_video",
                    models.FileField(
                        upload_to="",
                        validators=[
                            django.core.validators.FileExtensionValidator(
                                allowed_extensions=("mp4",)
                            )
                        ],
                        verbose_name="فیلم معرفی",
                    ),
                ),
                (
                    "header_video_explain",
                    models.TextField(verbose_name="توضیح در مورد معرفی ویدیو"),
                ),
                ("title_main", models.CharField(verbose_name="عنوان بدنه")),
                (
                    "title_main_explain",
                    models.TextField(verbose_name="توضیح عنوان بدنه"),
                ),
                ("footer_address", models.TextField(verbose_name="ادرس ها")),
                ("about_us_explain", models.TextField(verbose_name="درباره ما")),
                (
                    "copy_right_text",
                    models.CharField(max_length=255, verbose_name="متن کپی و رایت"),
                ),
                (
                    "is_main_settings",
                    models.BooleanField(verbose_name="تنظیم اصلی سایت باشد"),
                ),
                (
                    "phone",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=11),
                        help_text="برای وارد کردن چندین شماره تماس با کاما از هم دیگر جدا کنید",
                        size=5,
                        validators=[accounts.validators.MobileRegexValidator()],
                        verbose_name="شماره تماس با ما",
                    ),
                ),
                ("location", django.contrib.gis.db.models.fields.PointField(srid=4326)),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.CreateModel(
            name="TopStudent",
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
                    "student_name",
                    models.CharField(max_length=50, verbose_name="نام دانش اموز"),
                ),
                (
                    "student_image",
                    models.ImageField(
                        upload_to="main_settings/top_student",
                        verbose_name="عکس دانش اموز",
                    ),
                ),
                (
                    "explain",
                    models.CharField(
                        max_length=255, verbose_name="توضیح در مورد دانش اموز"
                    ),
                ),
                (
                    "is_publish",
                    models.BooleanField(default=True, verbose_name="انتشار در سایت"),
                ),
            ],
            options={
                "verbose_name": "برترین دانش اموزان",
                "verbose_name_plural": "برترین دانش اموزان",
                "db_table": "top_student",
            },
        ),
        migrations.CreateModel(
            name="SliderImage",
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
                    "slider_image_explain",
                    models.CharField(max_length=255, verbose_name="توضیح"),
                ),
                ("slider_url", models.URLField(verbose_name="ادرس اسلایدر")),
                (
                    "is_publish",
                    models.BooleanField(default=True, verbose_name="انتشار"),
                ),
                (
                    "image",
                    models.ManyToManyField(
                        related_name="main_slider_image", to="images.image"
                    ),
                ),
            ],
            options={
                "verbose_name": "عکس اسلایدر",
                "verbose_name_plural": "عکس اسلادر ها",
                "db_table": "slider_image",
            },
        ),
    ]
