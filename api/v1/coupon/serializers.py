from rest_framework import serializers

from apps.discount_app.models import Coupon


class ValidateCouponCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = ("code", "discount")
        read_only_fields = ("discount",)
