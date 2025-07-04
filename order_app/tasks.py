# import aiohttp
import string
import datetime
import random

from decouple import config
import asyncio
from celery import shared_task
from django.utils import timezone

from accounts.models import Student, Invitation, PrivateNotification
from discount_app.models import Coupon
# from education_system.dj_celery import app
from utils.send_sms import SmsIrPanel

# url = "https://rest.payamak-panel.com/api/SendSMS/SendSMS"

# headers = {
#     "Content-Type": "application/json",
# }

# TEXT = "کاربر گرامی ثبت شما با موفقیت انجام شد نام کاربری و رمز عبور شما به ترتیب برابر است با "

# create instance of sms panel .ir
instance = SmsIrPanel(
        api_key=config("SMS_IR_API_KEY", cast=str),
        base_url=config("SMS_IR_BASE_URL", cast=str),
    )


# @app.task(bind=True)
# def send_successfully_signup_async(self, phone_number, password):
#     async def _send_successfully_signup():
#         data = {
#             "username": config("SMS_USERNAME"),
#             "password": config("SMS_PASSWORD"),
#             "text": f"{TEXT} {phone_number} {password}",
#             "to": phone_number,
#             "from": config("SMS_PHONE_NUMBER"),
#         }
#         async with aiohttp.ClientSession(headers=headers) as session:
#             async with session.post(url, json=data) as response:
#                 res = await response.json()
#                 return res
#
#     return asyncio.run(_send_successfully_signup())

@shared_task(queue="course_signup")
def send_successfully_signup(phone, password, full_name):
    asyncio.run(
        instance.send_fast_multiple(
            phone=phone,
            value=[full_name, password],
            template_id=config("SMS_IR_COURSE_SIGNUP_TEMPLATE_ID", cast=int),
            template_name=["FULL_NAME","LOGIN"]
        )
    )

@shared_task(queue="coupon_send")
def coupon_send(phone, coupon_code):
    print("task done!")
    # asyncio.run(
    #     instance.send_fast_sms(
    #         phone=phone,
    #         value=coupon_code,
    #         template_id=config("SMS_IR_COUPON_SEND_TEMPLATE_ID", cast=int),
    #         template_name="coupon_send"
    #     )
    # )

@shared_task(queue="celery")
def process_referral(referral_code, mobile_phone):
    # check_referral_code if exits
    referral = Student.objects.filter(
        referral_code=referral_code
    ).only("student_number")

    # check referral_code is exiting
    if referral.exists():
        # get to_student
        to_student = Student.objects.filter(
            user__mobile_phone=mobile_phone
        ).only(
            "student_number"
        )

        # create invasion
        Invitation.objects.create(
            from_student=referral.first(),
            to_student=to_student.first()
        )
        # create coupon
        new_coupon = Coupon.objects.create(
            code=''.join(random.choices(
                string.ascii_letters + string.digits,
                k=20
            )),
            max_usage=1,
            valid_from=timezone.now(),
            valid_to=timezone.now() + datetime.timedelta(days=30),
            discount=30
        )
        # create notification
        notification = PrivateNotification.objects.create(
            user_id=referral.first().user_id,
            title="کد تخفیف جدید",
            body=(
                f"🎉 شما یک کد تخفیف جدید دریافت کرده‌اید!\n\n"
                f"کد تخفیف: {new_coupon.code}\n"
                f"مهلت استفاده: تا یک ماه آینده\n\n"
                # "برای استفاده، کافی است در زمان تسویه‌حساب این کد را وارد کنید."
            )
        )
        # send coupon_code into mobile_phone
        coupon_send.delay(
            phone=notification.user.mobile_phone,
            coupon_code=new_coupon.code
        )
