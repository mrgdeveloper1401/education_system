from rest_framework import viewsets, permissions, mixins
from django.utils import timezone

from discount_app.models import Discount, Coupon
from . import serializers


class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.filter(is_active=True)
    serializer_class = serializers.DiscountSerializer
    permission_classes = (permissions.IsAdminUser,)

    def get_queryset(self):
        queryset = super().get_queryset()

        content_type = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')

        if content_type and object_id:
            queryset = queryset.filter(
                content_type__model=content_type,
                object_id=object_id
            )

        return queryset


class FirstOneCouponViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    queryset = Coupon.objects.filter(
        is_active=True,
        valid_from__lte=timezone.now(),
        valid_to__gt=timezone.now(),
        # for_first=True,
        max_usage=1
    ).only(
        "code", "valid_to", "valid_from"
    )
    serializer_class = serializers.FirstOneCouponSerializer
