# Generated by Django 5.1.2 on 2024-12-15 20:20

import accounts.managers
import accounts.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="City",
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
                (
                    "city",
                    models.CharField(db_index=True, max_length=40, verbose_name="شهر"),
                ),
            ],
            options={
                "verbose_name": "شهر",
                "verbose_name_plural": "شهر ها",
                "db_table": "city",
            },
        ),
        migrations.CreateModel(
            name="Otp",
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
                (
                    "mobile_phone",
                    models.CharField(
                        max_length=11,
                        validators=[accounts.validators.MobileRegexValidator()],
                        verbose_name="mobile phone",
                    ),
                ),
                (
                    "code",
                    models.CharField(blank=True, max_length=6, verbose_name="code"),
                ),
                (
                    "expired_date",
                    models.DateTimeField(blank=True, verbose_name="expired date"),
                ),
            ],
            options={
                "verbose_name": "کد",
                "verbose_name_plural": "کد ها",
                "db_table": "otp_code",
                "ordering": ("created_at",),
            },
        ),
        migrations.CreateModel(
            name="State",
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
                (
                    "state_name",
                    models.CharField(max_length=30, unique=True, verbose_name="استان"),
                ),
            ],
            options={
                "verbose_name": "استان",
                "verbose_name_plural": "استان ها",
                "db_table": "state",
            },
        ),
        migrations.CreateModel(
            name="User",
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
                (
                    "last_login",
                    models.DateTimeField(
                        blank=True, null=True, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
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
                    "mobile_phone",
                    models.CharField(
                        max_length=11,
                        unique=True,
                        validators=[accounts.validators.MobileRegexValidator()],
                        verbose_name="mobile phone",
                    ),
                ),
                (
                    "first_name",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        max_length=30,
                        null=True,
                        verbose_name="first name",
                    ),
                ),
                (
                    "last_name",
                    models.CharField(
                        blank=True,
                        db_index=True,
                        max_length=30,
                        null=True,
                        verbose_name="last name",
                    ),
                ),
                (
                    "email",
                    models.EmailField(
                        blank=True,
                        db_index=True,
                        max_length=254,
                        null=True,
                        unique=True,
                        verbose_name="email address",
                    ),
                ),
                ("is_staff", models.BooleanField(db_index=True, default=False)),
                ("is_verified", models.BooleanField(default=False)),
                ("is_active", models.BooleanField(default=True)),
                (
                    "password",
                    models.CharField(
                        blank=True, max_length=128, null=True, verbose_name="password"
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        blank=True,
                        null=True,
                        upload_to="user_image/%Y/%m/%d",
                        validators=[accounts.validators.validate_upload_image_user],
                        verbose_name="عکس",
                    ),
                ),
                (
                    "second_mobile_phone",
                    models.CharField(
                        blank=True,
                        max_length=11,
                        null=True,
                        validators=[accounts.validators.MobileRegexValidator()],
                        verbose_name="شماره تماس دوم",
                    ),
                ),
                (
                    "nation_code",
                    models.CharField(
                        max_length=10,
                        null=True,
                        unique=True,
                        validators=[accounts.validators.NationCodeRegexValidator()],
                        verbose_name="کد ملی",
                    ),
                ),
                (
                    "address",
                    models.TextField(blank=True, null=True, verbose_name="ادرس"),
                ),
                (
                    "is_coach",
                    models.BooleanField(default=False, verbose_name="به عنوان مربی"),
                ),
                (
                    "birth_date",
                    models.DateField(blank=True, null=True, verbose_name="تاریخ نولد"),
                ),
                (
                    "gender",
                    models.CharField(
                        blank=True,
                        choices=[("male", "پسر"), ("Female", "دختر")],
                        max_length=6,
                        null=True,
                        verbose_name="gender",
                    ),
                ),
                (
                    "grade",
                    models.CharField(
                        blank=True,
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
                        null=True,
                        verbose_name="grade",
                    ),
                ),
                (
                    "school",
                    models.CharField(
                        blank=True, max_length=30, null=True, verbose_name="نام مدرسه"
                    ),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
                (
                    "city",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="student_city",
                        to="accounts.city",
                    ),
                ),
                (
                    "state",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="state",
                        to="accounts.state",
                        verbose_name="استان",
                    ),
                ),
            ],
            options={
                "verbose_name": "کاربر",
                "verbose_name_plural": "کاربران",
                "db_table": "users",
                "ordering": ("-created_at",),
            },
            managers=[
                ("objects", accounts.managers.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="RecycleUser",
            fields=[],
            options={
                "verbose_name": "کاربر پاک شده",
                "verbose_name_plural": "کاربران پاک شده",
                "proxy": True,
                "indexes": [],
                "constraints": [],
            },
            bases=("accounts.user",),
        ),
        migrations.CreateModel(
            name="Coach",
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
                ("bio", models.TextField(blank=True, null=True)),
                ("specialty", models.CharField(blank=True, max_length=255, null=True)),
                ("linkedin_url", models.URLField(blank=True, null=True)),
                (
                    "years_of_experience",
                    models.PositiveSmallIntegerField(blank=True, null=True),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="coach",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "استاد",
                "verbose_name_plural": "اساتید",
                "db_table": "coach",
            },
        ),
        migrations.AddField(
            model_name="city",
            name="state",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="cites",
                related_query_name="city",
                to="accounts.state",
                verbose_name="استان",
            ),
        ),
        migrations.CreateModel(
            name="Student",
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
                ("bio", models.TextField(blank=True, null=True)),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="student",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "دانش اموز",
                "verbose_name_plural": "دانش اموزان",
                "db_table": "student",
            },
        ),
        migrations.CreateModel(
            name="Ticket",
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
                ("ticker_body", models.TextField(verbose_name="متن تیکت")),
                (
                    "subject_ticket",
                    models.CharField(max_length=255, verbose_name="عنوان تیکت"),
                ),
                ("is_publish", models.BooleanField(default=True)),
                (
                    "user",
                    models.ForeignKey(
                        limit_choices_to={"is_active": True},
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="ticket",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "تیکت",
                "verbose_name_plural": "تیکت ها",
                "db_table": "ticket",
            },
        ),
        migrations.CreateModel(
            name="UserDevice",
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
                ("is_linux", models.BooleanField(default=False)),
                ("is_windows", models.BooleanField(default=False)),
                ("is_max", models.BooleanField(default=False)),
                ("is_iphone", models.BooleanField(default=False)),
                ("is_android", models.BooleanField(default=False)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="device",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "دستگاه های کاربر",
                "verbose_name_plural": "دستگاه های کاربران",
                "db_table": "user_device",
            },
        ),
        migrations.CreateModel(
            name="UserIp",
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
                ("user_ip", models.GenericIPAddressField()),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="ip",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "ای پی کاربر",
                "verbose_name_plural": "ای پی کاربران",
                "db_table": "user_ip",
            },
        ),
        migrations.CreateModel(
            name="UserLogins",
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
                ("success_login", models.PositiveIntegerField(default=0)),
                ("failed_login", models.PositiveIntegerField(default=0)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="logins",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "لاگین های کاربر",
                "verbose_name_plural": "لاگین های کاربران",
                "db_table": "user_logins",
            },
        ),
        migrations.AlterUniqueTogether(
            name="city",
            unique_together={("state", "city")},
        ),
    ]
