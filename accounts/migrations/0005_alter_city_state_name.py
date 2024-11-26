# Generated by Django 5.1.2 on 2024-11-18 05:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0004_alter_city_city"),
    ]

    operations = [
        migrations.AlterField(
            model_name="city",
            name="state_name",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="cites",
                related_query_name="city",
                to="accounts.state",
                verbose_name="استان",
            ),
        ),
    ]