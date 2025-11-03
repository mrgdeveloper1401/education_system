import asyncio
import httpx
from decouple import config

from utils.send_sms import SmsIrPanel

def headers():
    return {
        "Content-Type": "application/json",
        "x-api-key": config("SMS_IR_API_KEY", cast=str),
    }

async def async_send_otp_sms(phone, otp):
    async with httpx.AsyncClient() as client:
        # get url
        base_url = config("SMS_IR_BASE_URL", cast=str)
        verify_url = base_url + "send/verify"

        # data
        json = {
            "Mobile": phone,
            "TemplateId": config("SMS_IR_OTP_TEMPLATE_ID", cast=int),
            "parameters": [
                {
                    "name": "CODE",
                    "value": otp,
                }
            ]
        }

        # send request
        response = await client.post(
            url=verify_url,
            json=json,
            headers=headers(),
            timeout=15,
        )
        return response.json()


# asyncio.run(
#     send_otp_sms("09391640664",
#     "12345"
# ))