from .models import RequestLog
import json


class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # فیلتر کردن مقادیر قابل سریال‌سازی
        meta_data = {
            key: value
            for key, value in request.META.items()
            if isinstance(value, (str, int, float, bool))
        }

        # ذخیره لاگ
        RequestLog.objects.create(
            path=request.path,
            method=request.method,
            meta_data=json.dumps(meta_data)
        )

        response = self.get_response(request)
        return response
