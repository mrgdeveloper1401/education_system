import asyncio
import json

import httpx
from typing import List


class BasePanel:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url

    def header(self):
        raise NotImplementedError()

    def send_bulk(self, *args, **kwargs):
        raise NotImplementedError()

    @staticmethod
    async def send_post_request(address, json, headers):
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=address,
                json=json,
                headers=headers,
            )
            return response


class SmsIrPanel(BasePanel):
    def send_fast_sms(self, phone, value, template_id, template_name):
        """
        phone --> phone number:
        value --> مقدار کلید تعیین شده برای جایگزینی در قالب پیامک (حداکثر 25 کاراکتر):
        template_id --> شناسه قالب (قالب ها از طریق پنل قابل تعریف و مدیریت می‌باشند):
        template_name: کلید تعیین شده در قالب (بدون در نظر گرفتن # در ابتدا و انتهای آن)
        """
        url = self.base_url + "send/verify"
        data = {
            "Mobile": phone,
            "TemplateId": template_id,
            "parameters": [
                {
                    "name": template_name,
                    "value": value
                }
            ]
        }
        return self.send_post_request(url, data, self.header())

    def send_fast_multiple(self, phone: str, value: list, template_id: int, template_name: list):
        """
        در این جا میتوان چندین متغییر رو فرستاد
        phone --> phone number:
        value --> مقدار کلید تعیین شده برای جایگزینی در قالب پیامک (حداکثر 25 کاراکتر):
        template_id --> شناسه قالب (قالب ها از طریق پنل قابل تعریف و مدیریت می‌باشند):
        template_name: کلید تعیین شده در قالب (بدون در نظر گرفتن # در ابتدا و انتهای آن)
        """
        url = self.base_url + "send/verify"
        data = {
            "Mobile": phone,
            "TemplateId": template_id,
            "parameters": [
                {
                    "name": j,
                    "value": i
                }
                for i, j in zip(value, template_name)
            ]
        }
        # print(data)
        # return data
        return self.send_post_request(url, data, self.header())

    def send_bulk(self, line_number, message_text, mobiles: List[str], send_date_time=None):
        """
        line_number --> شماره خط ارسالی
        message_text --> متن پیام
        mobiles --> شماره ها
        send_date_time --> زمان ارسال پیام
        """
        url = self.base_url + "/send/bulk/"
        data = {
            "lineNumber": line_number,
            "MessageText": message_text,
            "Mobiles": mobiles,
        }
        data = json.dumps(data)
        # print(data)
        return self.send_post_request(url, data, self.header())

    def header(self):
        return {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
        }


if __name__ == "__main__":
    from decouple import config

    s1 = SmsIrPanel(
        api_key=config("SMS_IR_API_KEY", cast=str),
        base_url=config("SMS_IR_BASE_URL", cast=str),
    )

    # print(
    #     asyncio.run(
    #         s1.send_fast_sms(
    #             phone="09391640664",
    #             value="1234",
    #             template_id=config("SMS_IR_FORGET_PASSWORD_TEMPLATE_ID", cast=int),
    #             template_name="CODE"
    #         )
    #     )
    # )

    # print(
    #     asyncio.run(
    #         s1.send_fast_sms(
    #             phone="09391640664",
    #             value=["محمد گودرزی", "09391640664"],
    #             template_id=config("SMS_IR_COURSE_SIGNUP_TEMPLATE_ID", cast=int),
    #             template_name=["FULL_NAME", "CODE"]
    #         )
    #     )
    # )

    # print(
    #     asyncio.run(
    #         s1.send_fast_multiple(
    #             phone="09391640664",
    #             value=["محمد گودرزی", "09391640664"],
    #             template_name=["FULL_NAME", "LOGIN"],
    #             template_id=config("SMS_IR_COURSE_SIGNUP_TEMPLATE_ID", cast=int)
    #     )
    # )
    # )

    # print(asyncio.run(s1.send_verify(
    #     phone="9391640664",
    #     value="123456",
    #     template_id=123456,
    #     template_name="CODE"
    # )))
