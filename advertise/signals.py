from datetime import datetime, timedelta

from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import DefineAdvertise


def create_interval(sender, instance, created, **kwargs):
    if created:
        start = instance.start_time
        convert = datetime.combine(datetime.today(), start)
        new_time = convert + timedelta(minutes=instance.interval_minutes)