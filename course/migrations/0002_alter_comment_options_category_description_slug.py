# Generated by Django 5.1.5 on 2025-05-31 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('course', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comment',
            options={'ordering': ('created_at',)},
        ),
        migrations.AddField(
            model_name='category',
            name='description_slug',
            field=models.SlugField(allow_unicode=True, blank=True, null=True),
        ),
    ]
