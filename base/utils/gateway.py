import httpx


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


class Zibal(Gateway):
    ZIBAL_REQUEST_URL = "https://gateway.zibal.ir/v1/request"
    ZIBAL_VERIFY_PAYMENT = "https://gateway.zibal.ir/v1/verify"

    def __init__(self, api_key, call_back_url, amount=None):
        self.amount = amount
        super().__init__(api_key, call_back_url)

    @property
    def headers(self):
        return {"Content-Type": "application/json"}

    def request_url(self):
        data = {
            "merchant": self.api_key,
            "callbackUrl": self.call_back_url,
            "amount": self.amount,
        }
        response = httpx.post(
            url=self.ZIBAL_REQUEST_URL, headers=self.headers, json=data
        )
        return response.json()

    def verify(self, *args, **kwargs):
        data = {"merchant": self.api_key, "trackId": kwargs.get("track_id")}
        response = httpx.post(
            url=self.ZIBAL_VERIFY_PAYMENT, headers=self.headers, json=data
        )
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
