# Generated by Django 5.1.2 on 2024-11-04 22:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("course", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="course",
            name="course_parent",
        ),
    ]
