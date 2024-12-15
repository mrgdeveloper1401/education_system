# Generated by Django 5.1.2 on 2024-12-13 15:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("course", "0005_section_is_available_alter_section_video"),
    ]

    operations = [
        migrations.AddField(
            model_name="practice",
            name="expired_practice",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="practice",
            name="practice_title",
            field=models.CharField(
                default=0, max_length=255, verbose_name="عنوان تمرین"
            ),
            preserve_default=False,
        ),
    ]