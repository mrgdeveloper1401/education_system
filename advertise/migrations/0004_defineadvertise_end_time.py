# Generated by Django 5.1.2 on 2024-11-21 08:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("advertise", "0003_remove_defineadvertise_end_time"),
    ]

    operations = [
        migrations.AddField(
            model_name="defineadvertise",
            name="end_time",
            field=models.TimeField(default="00:00:00", verbose_name="ساعت پایان"),
            preserve_default=False,
        ),
    ]
