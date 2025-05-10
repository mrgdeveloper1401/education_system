from rest_framework import viewsets, mixins, permissions

from subscription_app.models import Subscription
from . import serializers
from ..course.paginations import CommonPagination


class SubscriptionViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CommonPagination

    def get_queryset(self):
        return Subscription.objects.filter(
            user=self.request.user
        ).defer("is_deleted", "deleted_at").select_related("course__category")
