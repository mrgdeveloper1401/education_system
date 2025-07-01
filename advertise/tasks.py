import asyncio

from celery import shared_task
from decouple import config

from utils.send_sms import SmsIrPanel

url = "https://rest.payamak-panel.com/api/SendSMS/SendSMS"
headers = {
    "Content-Type": "application/json",
}

TEXT_ADVERTISE = "کاربر گرامی درخواست مشاوه شما ثبت گردید− تاریخ مشاوره برابر است با: "

instance = SmsIrPanel(api_key=config("SMS_IR_API_KEY", cast=str), base_url=config("SMS_IR_BASE_URL", cast=str))


@shared_task(queue="advertise")
def send_sms_accept_advertise(phone, advertise_date):
    # data = {
    #     "username": config("SMS_USERNAME"),
    #     "password": config("SMS_PASSWORD"),
    #     "text": TEXT_ADVERTISE + advertise_date,
    #     "to": phone,
    #     "from": config("SMS_PHONE_NUMBER"),
    # }
    # response = requests.post(url, headers=headers, json=data)
    # return response.json()
    asyncio.run(
        instance.send_fast_sms(
            phone=phone,
            value=advertise_date,
            template_id=config("SMS_IR_ADVERTISE_TEMPLATE_ID", cast=int),
            template_name="DATE",
        )
    )


# print(send_sms_accept_advertise.delay("09391640664", "2025/10/12"))