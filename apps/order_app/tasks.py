import string
import datetime
import random

from celery import shared_task
from decouple import config
from django.utils import timezone

from apps.account_app.models import Student, Invitation, PrivateNotification
from apps.discount_app.models import Coupon
from base.utils.send_sms import send_sms_signup_course, send_sms

COUPON_SEND_TEMPLATE_ID = config(
    "SMS_IR_COUPON_SEND_TEMPLATE_ID", cast=int
)  # todo, move into config file


@shared_task(bind=True, queue="course_signup", max_retries=2)
def send_successfully_signup_task(
    self, phone, template_id, template_name, password, full_name
):
    try:
        values = {"full_name": full_name, "password": password}
        return send_sms_signup_course(
            template_id=template_id,
            mobile=phone,
            template_name=template_name,
            values=values,
        )
    except Exception as e:
        self.retry(exc=e, countdown=10)


@shared_task(bind=True, queue="coupon_send", max_retries=2)
def coupon_send_task(self, phone, coupon_code):
    try:
        return send_sms(
            template_id=COUPON_SEND_TEMPLATE_ID,
            template_name="coupon_send",
            mobile=phone,
            value=coupon_code,
        )
    except Exception as e:
        self.retry(exc=e, countdown=10)


@shared_task(queue="celery")
def process_referral(referral_code, mobile_phone):
    # check_referral_code if exits
    referral = Student.objects.filter(referral_code=referral_code).only(
        "student_number"
    )

    # check referral_code is exiting
    if referral.exists():
        # get to_student
        to_student = Student.objects.filter(user__mobile_phone=mobile_phone).only(
            "student_number"
        )

        # create invasion
        Invitation.objects.create(
            from_student=referral.first(), to_student=to_student.first()
        )
        # create coupon
        new_coupon = Coupon.objects.create(
            code="".join(random.choices(string.ascii_letters + string.digits, k=20)),
            max_usage=1,
            valid_from=timezone.now(),
            valid_to=timezone.now() + datetime.timedelta(days=30),
            discount=30,
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
            ),
        )
        # send coupon_code into mobile_phone
        coupon_send_task.delay(
            phone=notification.user.mobile_phone, coupon_code=new_coupon.code
        )
