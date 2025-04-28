from rest_framework import serializers

from order_app.models import Order


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("course", "price", "mobile_phone")
