# Generated by Django 5.1.2 on 2024-12-06 14:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("advertise", "0002_alter_consultationrequest_topic"),
    ]

    operations = [
        migrations.AlterField(
            model_name="consultationrequest",
            name="topic",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
