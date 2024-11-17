# Generated by Django 5.1.2 on 2024-11-17 15:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("accounts", "0001_initial"),
        ("departments", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="ticket",
            name="department",
            field=models.ForeignKey(
                limit_choices_to={
                    "user__is_active": True,
                    "user__is_deleted": False,
                    "user__is_staff": True,
                },
                on_delete=django.db.models.deletion.PROTECT,
                related_name="admin_ticket",
                to="departments.department",
                verbose_name="کاربر ادمین",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="city",
            unique_together={("state_name", "city")},
        ),
    ]