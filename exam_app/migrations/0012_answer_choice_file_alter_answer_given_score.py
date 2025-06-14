# Generated by Django 5.1.5 on 2025-06-07 21:06

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exam_app', '0011_remove_choice_choice_file'),
    ]

    operations = [
        migrations.AddField(
            model_name='answer',
            name='choice_file',
            field=models.FileField(blank=True, help_text='در صورتی که نیاز به ارسال فایل هست میتوانید فایل رو ارسال کیند', null=True, upload_to='choice_exam/file/%Y/%m/%d'),
        ),
        migrations.AlterField(
            model_name='answer',
            name='given_score',
            field=models.PositiveSmallIntegerField(blank=True, help_text='نمره اختصاص داده شده توسط تصحیح کننده', null=True, validators=[django.core.validators.MinValueValidator(0)]),
        ),
    ]
