from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.permissions import IsAuthenticated

from cart_app.models import Cart, CartItem, Order
from . import serializers


class CartViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CartSerializer
    queryset = Cart.objects.filter(is_active=True)


class CartItemViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AddCartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk'], is_active=True).select_related("plan")

    def get_serializer_context(self):
        return {'cart_pk': self.kwargs['cart_pk']}


class OrderViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin,
                   viewsets.GenericViewSet):
    serializer_class = serializers.OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {"user": self.request.user}

    def get_queryset(self):
        return Order.objects.filter(is_active=True, user=self.request.user)