from rest_framework import viewsets

from cart_app.models import Cart, CartItem
from . import serializers


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CartSerializer
    queryset = Cart.objects.all()


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AddCartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related("plan")

    def get_serializer_context(self):
        return {'cart_pk': self.kwargs['cart_pk']}
