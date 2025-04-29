from django.dispatch import receiver
from django.db.models.signals import post_save

from accounts.models import User
from . import models
from .tasks import send_successfully_signup_async


@receiver(post_save, sender=models.CourseSignUp)
def create_student_profile(sender, instance, created, **kwargs):
    if created:
        get_user = User.objects.filter(mobile_phone=instance.mobile_phone).only("mobile_phone")
        if not get_user:
            User.objects.create_user(
                mobile_phone=instance.mobile_phone,
                password=instance.mobile_phone,
                first_name=instance.first_name,
                last_name=instance.last_name,
            )
            send_successfully_signup_async.delay(instance.mobile_phone)
