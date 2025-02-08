from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from subscription_app.models import Subscription

from . import serializers


# class SubscriptionViewSet(viewsets.ModelViewSet):
#     serializer_class = serializers.SubscriptionSerializer
#     permission_classes = [IsAuthenticated]
#
#     def get_permissions(self):
#         if self.request.method not in SAFE_METHODS:
#             return [IsAdminUser()]
#         return super().get_permissions()
#
#     def get_queryset(self):
#         return Subscription.objects.filter(user=self.request.user)
#
#     def get_serializer_context(self):
#         return {"user": self.request.user}
#
#     def get_serializer_class(self):
#         if self.action == "create":
#             return serializers.CreateSubscriptionSerializer
#         if self.action in ['update', 'partial_update']:
#             return serializers.UpdateSubscriptionSerializer
#         return super().get_serializer_class()


class SubscriptionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.SubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Subscription.objects.filter(user=self.request.user, is_active=True)
