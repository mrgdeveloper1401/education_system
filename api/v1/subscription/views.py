from rest_framework import viewsets, permissions

from subscription_app.models import Subscription
from . import serializers
from ..course.paginations import CommonPagination


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    status --> active / expired / pending / canceled / trial \n
    pagination --> 20 item \n
    search --> ?status=status
    """
    serializer_class = serializers.SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CommonPagination

    def get_queryset(self):
        return Subscription.objects.filter(
            mobile_phone=self.request.user.mobile_phone
        ).defer("is_deleted", "deleted_at").select_related("course__category")

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = (permissions.AllowAny,)
        if self.request.method == ['PATCH', "PUT", "DELETE"]:
            self.permission_classes = (permissions.IsAdminUser,)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CreateSubscriptionSerializer
        return super().get_serializer_class()

    def filter_queryset(self, queryset):
        status = self.request.query_params.get("status", None)

        if status:
            return queryset.filter(status=status)
        return queryset
