import requests
from decouple import config

url = "https://rest.payamak-panel.com/api/SendSMS/SendSMS"

headers = {
    "Content-Type": "application/json",
}

data = {
  "username": config("SMS_USERNAME", cast=str),
  "password": config("SMS_PASSWORD", cast=str),
  "text": "test send api",
  "to": "09391640664",
  "from": config("SMS_PHONE_NUMBER", cast=str),
}

def send_sms_otp_code(phone, code):
  res = requests.post(url=url, headers=headers, json=data)
  return res
