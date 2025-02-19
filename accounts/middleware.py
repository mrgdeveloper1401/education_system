from .models import RequestLog
from django.core.cache import cache

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


class UserCacheMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if user.is_authenticated:
            cache_key = f'user_{user.id}'
            cached_user = cache.get(cache_key)
            if cached_user is None:
                cached_user = {
                    "id": user.id,
                    "mobile_phone": user.mobile_phone,
                }
                cache.set(cache_key, cached_user, timeout=3600)
            request.cached_user = cached_user
        print(user)
        response = self.get_response(request)
        return response
