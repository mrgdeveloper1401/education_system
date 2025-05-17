import requests
from decouple import config
import json


class Gateway:
    def __init__(self, api_key, call_back_url):
        self.api_key = api_key
        self.call_back_url = call_back_url

    def headers(self):
        raise NotImplementedError

    def request_url(self):
        raise NotImplementedError

    def verify(self, *args, **kwargs):
        raise NotImplementedError

    def redirect_url(self, token: str):
        """ساخت آدرس نهایی هدایت کاربر به صفحه پرداخت"""
        raise NotImplementedError


class BitPay(Gateway):
    request_endpoint = "https://bitpay.ir/payment/gateway-send"
    verify_endpoint = "https://bitpay.ir/payment/gateway-result-second"
    # TODO, bug fix verify payment argument, auto get api key and redirect url
    def __init__(self, api_key, call_back_url=None, amount=None, order_id=None, name=None, email=None, description=None):
        super().__init__(api_key, call_back_url)
        self.amount = amount
        self.order_id = order_id
        self.name = name
        self.email = email
        self.description = description

    @property
    def headers(self):
        return {
            "Content-Type": "application/x-www-form-urlencoded",
        }

    def request_url(self):
        data = {
            'api': self.api_key,
            'redirect': self.call_back_url,
            'amount': self.amount,
            'factorId': self.order_id,
            'name': self.name,
            'email': self.email,
            'description': self.description,
        }

        response = requests.post(url=self.request_endpoint, data=data, headers=self.headers)
        response_data = response.json()
        return {
            "payment_url": self.redirect_url(response_data),
            "token": response_data,
        }

    def redirect_url(self, token: str):
        return f"https://bitpay.ir/payment/gateway-{token}"

    def verify(self, trans_id, id_get):
        data = {
            "api": self.api_key,
            "trans_id": trans_id,
            "id_get": id_get,
            "json": 1
        }

        response = requests.post(url=self.verify_endpoint, data=data, headers=self.headers)
        return response.json()


# x1 = BitPay(
#     api_key=config("GATEWAY_ID"),
#     call_back_url=config("REDIRECT_URL"),
#     amount=50000,
#     order_id="1234",
#     name="Mohammad Goodarzi",
#     email="mysum325g@gmail.com",
#     description="Test payment link"
# )
#
# result = x1.request_url()
# print(result > 0)
# print(result)
