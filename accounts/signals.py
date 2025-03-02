from uuid import uuid4

from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone
from .models import User, Coach, Student


@receiver(post_save, sender=User)
def create_coach(sender, instance, created, **kwargs):
    instance_number = f"s{str(timezone.now().date().year)[-2:]}{str(uuid4().int)[:8]}"
    if created:
        if instance.is_coach:
            Coach.objects.get_or_create(user=instance, coach_number=instance_number.replace("s", "c"))
        if instance.is_student:
            Student.objects.get_or_create(user=instance, student_number=instance_number)
