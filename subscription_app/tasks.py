from datetime import timedelta
from celery import shared_task
from django.utils import timezone
from decouple import config

from subscription_app.models import Subscription
from utils.send_sms import SmsIrPanel


@shared_task
def send_sms_before_expire_subscription():
    age_one_weekend = timezone.now() + timedelta(days=7)
    subs = Subscription.objects.filter(
        end_date__lte=age_one_weekend,
    )
    if subs:
        sms_ir = SmsIrPanel(
            api_key=config("SMS_IR_API_KEY", cast=str),
            base_url="https://api.sms.ir/v1/send/bulk"
        )
        sms_ir.send_bulk(
            # شماره خط ارسالی
            line_number=config("SMS_IR_LINE_NUMBER", cast=str),
            message_text="کاربر گرامی از اشتراک شما یک هفته باقی مانده هست در صورت نیاز به تمدید ان اقدام فرمایید",
            # TODO , performance mobile field
            mobiles=[i.user.mobile_phone for i in subs],
        )
