from typing import List

from decouple import config
import asyncio
from celery import shared_task

from utils.send_sms import SmsIrPanel


TEXT_OTP_CODE = "کاربر گرامی کد تایید شما برابر است با "

TEXT_COUPON_CODE = "کاربر گرامی ثبت نام شما با موقیت انجام شد کد تخفیف شما برابر با است با: "

url = "https://rest.payamak-panel.com/api/SendSMS/SendSMS"

headers = {
    "Content-Type": "application/json",
}

instance = SmsIrPanel(api_key=config("SMS_IR_API_KEY", cast=str), base_url=config("SMS_IR_BASE_URL", cast=str))


@shared_task(queue='sms_otp')
def send_sms_otp_code(phone, code):
    asyncio.run(instance.send_fast_sms(
        phone=phone,
        value=code,
        template_id=config("SMS_IR_OTP_TEMPLATE_ID", cast=str),
        template_name="CODE"
    ))


@shared_task
def send_coupon_when_user_referral_signup(phone, coupon_code):
    asyncio.run(
        instance.send_fast_sms(
            phone=phone,
            value=coupon_code,
            template_id=config("SMS_IR_COUPON_TEMPLATE_ID", cast=str),
            template_name="coupon_user_referral_signup"
        )
    )


@shared_task
def send_multiple_message(phone: List[str], message):
    asyncio.gather(
        *instance.send_bulk(
            line_number=config("SMS_IR_LINE_NUMBER", cast=str),
            message_text=message,
            mobiles=phone,
            send_date_time=None
        )
    )
