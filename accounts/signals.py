from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import User, Coach, Student


@receiver(post_save, sender=User)
def create_coach(sender, instance, created, **kwargs):
    if instance.is_coach:
        Coach.objects.get_or_create(user=instance)
    if instance.is_student:
        Student.objects.get_or_create(user=instance)
