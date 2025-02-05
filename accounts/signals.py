from uuid import uuid4

from django.dispatch import receiver
from django.db.models.signals import post_save
from datetime import datetime
from .models import User, Coach, Student


@receiver(post_save, sender=User)
def create_coach(sender, instance, created, **kwargs):
    if instance.is_coach:
        Coach.objects.get_or_create(user=instance)
    if instance.is_student:
        std_number = f"s{str(datetime.today().year)[-2:]}{str(uuid4)[-6:]}"
        Student.objects.get_or_create(user=instance, student_number=std_number)
