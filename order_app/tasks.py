import aiohttp
from decouple import config
import asyncio

from education_system.dj_celery import app


url = "https://rest.payamak-panel.com/api/SendSMS/SendSMS"

headers = {
    "Content-Type": "application/json",
}

TEXT = "کاربر گرامی ثبت شما با موفقیت انجام شد نام کاربری و رمز عبور شما به ترتیب برابر است با "

@app.task(bind=True)
def send_successfully_signup_async(self, phone_number, password):
    async def _send_successfully_signup():
        data = {
            "username": config("SMS_USERNAME"),
            "password": config("SMS_PASSWORD"),
            "text": f"{TEXT} {phone_number} {password}",
            "to": phone_number,
            "from": config("SMS_PHONE_NUMBER"),
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.post(url, json=data) as response:
                res = await response.json()
                return res

    return asyncio.run(_send_successfully_signup())
