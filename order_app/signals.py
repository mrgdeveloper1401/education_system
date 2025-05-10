from django.dispatch import receiver
from django.db.models.signals import post_save

from accounts.models import User, Otp
from utils.create_random import create_password_random
from . import models
from .tasks import send_successfully_signup_async
from accounts.tasks import send_sms_otp_code_async


@receiver(post_save, sender=models.CourseSignUp)
def create_student_profile(sender, instance, created, **kwargs):
    if created:
        get_user = User.objects.filter(mobile_phone=instance.mobile_phone).only("mobile_phone")
        if not get_user:
            password = create_password_random(phone=instance.mobile_phone[:4])
            User.objects.create_user(
                mobile_phone=instance.mobile_phone,
                password=password,
                first_name=instance.first_name,
                last_name=instance.last_name,
            )
            send_successfully_signup_async.delay(instance.mobile_phone, password)
        else:
            otp = Otp.objects.create(mobile_phone=instance.mobile_phone)
            send_sms_otp_code_async.delay(otp.mobile_phone, otp.code)
