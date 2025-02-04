from django.http import JsonResponse
from .models import RequestLog


def log_request_view(request):
    RequestLog.objects.create(
        path=request.path,
        method=request.method,
        meta_data=dict(request.META)
    )

    return JsonResponse({"message": "Request logged successfully"})
