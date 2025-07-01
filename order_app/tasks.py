# import aiohttp
from decouple import config
import asyncio
from celery import shared_task

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
