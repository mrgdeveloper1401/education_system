from rest_framework import serializers

from discount_app.models import Coupon


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        exclude = ("is_deleted", "deleted_at")
