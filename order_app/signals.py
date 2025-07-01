# from django.dispatch import receiver
# from django.db.models.signals import post_save
#
# from accounts.models import User, Otp
# from . import models
# from .tasks import send_successfully_signup
# from accounts.tasks import send_sms_otp_code
#
#
# @receiver(post_save, sender=models.CourseSignUp)
# def create_student_profile(sender, instance, created, **kwargs):
#     if created:
#         # get user
#         get_user = User.objects.filter(mobile_phone=instance.mobile_phone).only("mobile_phone")
#
#         # check user
#         if not get_user:
#
#             # create random_password
#             # password = create_password_random(phone=instance.mobile_phone[:4])
#
#             # create user
#             User.objects.create_user(
#                 mobile_phone=instance.mobile_phone,
#                 # password=password,
#                 password=instance.mobile_phone,
#                 first_name=instance.first_name,
#                 last_name=instance.last_name,
#             )
#             # send sms
#             send_successfully_signup.delay(instance.mobile_phone, instance.mobile_phone)
#         else:
#
#             # create otp
#             otp = Otp.objects.create(mobile_phone=instance.mobile_phone)
#
#             # send sms
#             send_sms_otp_code.delay(otp.mobile_phone, otp.code)
