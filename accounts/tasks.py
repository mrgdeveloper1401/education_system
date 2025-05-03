import aiohttp
from decouple import config
import asyncio

from education_system.dj_celery import app


TEXT_OTP_CODE = "کاربر گرامی کد تایید شما برابر است با: "
url = "https://rest.payamak-panel.com/api/SendSMS/SendSMS"
headers = {
    "Content-Type": "application/json",
}


@app.task(bind=True)
def send_sms_otp_code_async(self, phone, code):
    async def _send_sms():
        data = {
            "username": config("SMS_USERNAME"),
            "password": config("SMS_PASSWORD"),
            "text": TEXT_OTP_CODE + str(code),
            "to": phone,
            "from": config("SMS_PHONE_NUMBER"),
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url, json=data) as response:
                res = await response.json()
                return res

    return asyncio.run(_send_sms())
