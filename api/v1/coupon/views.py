from django.utils import timezone
from rest_framework import views, exceptions, response

from . import serializers
from discount_app.models import Coupon


class ValidateCouponCodeView(views.APIView):
    """
    send code into query_params
    ?code=code
    """
    serializer_class = serializers.ValidateCouponCodeSerializer

    def get(self, request):
        code = request.query_params.get("code")
        now = timezone.now()

        coupon = Coupon.objects.filter(
            code=code,
            is_active=True,
            valid_from__lte=now,  # تاریخ شروع باید قبل از الان باشد
            valid_to__gte=now,  # تاریخ پایان باید بعد از الان باشد
        ).only(
            "code",
            "is_active",
            "valid_from",
            "valid_to",
            "discount"
        ).last()

        if not coupon:
            raise exceptions.NotFound("coupon code not exists")

        serializer = self.serializer_class(coupon)
        return response.Response(serializer.data)
