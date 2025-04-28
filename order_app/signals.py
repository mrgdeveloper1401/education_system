from django.dispatch import receiver
from django.db.models.signals import post_save

from accounts.models import User
from . import models


@receiver(post_save, sender=models.Order)
def create_student_profile(sender, instance, created, **kwargs):
    if created:
        get_user = User.objects.filter(mobile_phone=instance.mobile_phone).only("mobile_phone")
        if not get_user:
            User.objects.create_user(
                mobile_phone=instance.mobile_phone,
                password=instance.password,
            )
