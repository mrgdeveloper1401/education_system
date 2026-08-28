import httpx
from decouple import config
from rest_framework.exceptions import ValidationError

X_API_KEY = config('SMS_IR_API_KEY', cast=str)


def request_error(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except httpx.TimeoutException as t:
            raise ValidationError(detail=str(t), code='timeout')
        except httpx.ConnectError as c:
            raise ValidationError(detail=str(c), code='connect')
        except httpx.NetworkError as n:
            raise ValidationError(detail=str(n), code='network')
        except Exception as e:
            raise ValidationError(detail=str(e), code='error')

    return wrapper

@request_error
def send_sms(template_id, mobile, template_name, value):
    url = 'https://api.sms.ir/v1/send/verify'
    data = {
        'mobile': mobile,
        "templateId": int(template_id),
        "parameters": [
            {
                "name": template_name,
                "value": value
            }
        ]
    }
    headers = {
        "x-api-key": X_API_KEY
    }
    response = httpx.post(url, json=data, headers=headers)
    return response.json()

@request_error
def send_sms_signup_course(template_id, mobile, template_name, values: dict):
    url = 'https://api.sms.ir/v1/send/verify'
    data = {
        'mobile': mobile,
        "templateId": int(template_id),
        "parameters": [
            {
                "name": template_name,
                "value": j
            }
            for i, j in values.items()
        ]
    }
    headers = {
        "x-api-key": X_API_KEY
    }
    response = httpx.post(url, json=data, headers=headers)
    return response.json()