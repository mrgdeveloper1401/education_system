import requests


class BasePanel:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url

    def header(self):
        pass

    def send_bulk(self):
        pass

    @staticmethod
    def send_post_request(address, json, headers):
        response = requests.post(address, json=json, headers=headers)
        return response


class SmsIrPanel(BasePanel):
    def send_verify(self, phone, value, template_id, template_name):
        """
        phone --> phone number:
        value --> مقدار کلید تعیین شده برای جایگزینی در قالب پیامک (حداکثر 25 کاراکتر):
        template_id --> شناسه قالب (قالب ها از طریق پنل قابل تعریف و مدیریت می‌باشند):
        template_name: کلید تعیین شده در قالب (بدون در نظر گرفتن # در ابتدا و انتهای آن)
        """
        url = self.base_url + "v1/send/verify"
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


    def send_bulk(self, line_number, message_text, mobiles: list, send_date_time=None):
        url = self.base_url + "v1/send/bulk"
        data = {
            "lineNumber": line_number,
            "messageText": message_text,
            "mobiles": mobiles,
        }
        return self.send_post_request(url, data, self.header())

    def header(self):
        return {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
        }


s1 = SmsIrPanel(
    api_key="0a9fBsTECzRq86Xu8FlBf3ZyT6StN9wSJPgEBpfjTXQlbWXb",
    base_url="https://api.sms.ir/"
)
# print(s1.header())
# print(s1.send_verify("lkghnmlk", "v1/send/verify"))
