from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from cart_app.models import Cart, CartItem
from subscription_app.models import Plan


class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id', "created_at"]
        read_only_fields = ['id']


class AddCartItemSerializer(serializers.ModelSerializer):
    plan_id = serializers.IntegerField()
    plan = serializers.CharField(read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', "plan", "plan_id"]

    def validate(self, attrs):
        plan_id = attrs.get('plan_id')
        get_object_or_404(Plan, pk=plan_id)
        return attrs

    def create(self, validated_data):
        cart_id = self.context['cart_pk']
        return CartItem.objects.create(cart_id=cart_id, plan_id=validated_data['plan_id'])