from rest_framework import serializers
from rest_framework.validators import ValidationError
from django.utils.translation import gettext_lazy as _

from coupons.models import Coupon, Discount


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        exclude = ['deleted_at', "is_deleted"]


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        exclude = ['deleted_at', "is_deleted"]
