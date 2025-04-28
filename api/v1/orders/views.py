from rest_framework import viewsets, mixins

from . import serializers
from order_app.models import Order


class OrderViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = serializers.OrderSerializer
    queryset = Order.objects.only("course", "price", "mobile_phone")
