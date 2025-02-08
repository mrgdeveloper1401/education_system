from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from django.utils.translation import gettext_lazy as _

from cart_app.models import Cart, CartItem, Order, OrderItem
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

    def validate_plan_id(self, data):
        get_object_or_404(Plan, pk=data)
        return data

    def validate(self, attrs):
        cart_id = self.context["cart_pk"]
        plan_id = attrs.get("plan_id")
        cart = Cart.objects.get(id=cart_id)
        cart_item = cart.items.filter(plan=plan_id)
        if cart_item:
            raise serializers.ValidationError({"message": _("plan already exists")})
        return attrs

    def create(self, validated_data):
        cart_id = self.context['cart_pk']
        return CartItem.objects.create(cart_id=cart_id, plan_id=validated_data['plan_id'])


class OrderSerializer(serializers.Serializer):
    cart_id = serializers.CharField()

    def validate_cart_id(self, data):
        cart = get_object_or_404(Cart, pk=data)
        if cart.is_added:
            raise serializers.ValidationError({"message": _("cart already added to order")})
        return cart
    
    def create(self, validated_data):
        user = self.context['user']
        cart = validated_data['cart_id']
        order = Order.objects.create(
            user=user, cart=cart
        )
        cart.is_added = True
        cart.save()

        cart_item = cart.items.all()
        list_order_item = []
        for item in cart_item:
            list_order_item.append(OrderItem(
                order=order,
                plan=item.plan,
                price=item.plan.price,
            ))
        OrderItem.objects.bulk_create(list_order_item)
        return order
