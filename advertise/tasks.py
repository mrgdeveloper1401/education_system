from celery import shared_task
import requests
from decouple import config


url = "https://rest.payamak-panel.com/api/SendSMS/SendSMS"
headers = {
    "Content-Type": "application/json",
}

TEXT_ADVERTISE = "کاربر گرامی درخواست مشاوه شما ثبت گردید− تاریخ مشاوره برابر است با: "


@shared_task
def send_sms_accept_advertise(phone, advertise_date):
    data = {
        "username": config("SMS_USERNAME"),
        "password": config("SMS_PASSWORD"),
        "text": TEXT_ADVERTISE + advertise_date,
        "to": phone,
        "from": config("SMS_PHONE_NUMBER"),
    }
    response = requests.post(url, headers=headers, json=data)
    return response.json()


# print(send_sms_accept_advertise.delay("09391640664", "2025/10/12"))