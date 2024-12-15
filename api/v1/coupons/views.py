from rest_framework import viewsets
from rest_framework import permissions

from . import serializers
from coupons.models import Coupon, Discount
from .serializers import DiscountSerializer


class CouponViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CouponSerializer
    queryset = Coupon.objects.all()
    permission_classes = [permissions.IsAdminUser]


class DiscountViewSet(viewsets.ModelViewSet):
    serializer_class = DiscountSerializer
    queryset = Discount.objects.select_related('course')
    permission_classes = [permissions.IsAdminUser]

