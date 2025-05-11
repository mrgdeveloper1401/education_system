from rest_framework import viewsets, permissions

from subscription_app.models import Subscription
from . import serializers
from ..course.paginations import CommonPagination


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    status --> active / expired / pending / canceled / trial \n
    pagination --> 20 item \n
    search --> ?status=status   | ?phone=mobile_phone
    """
    serializer_class = serializers.SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CommonPagination

    def get_queryset(self):
        return Subscription.objects.select_related("user", "crud_course_type__course__category").only(
            "course__course_name",
            "course__category__category_name",
            "crud_course_type__course",
            "price",
            "status",
            "user__mobile_phone",
            "user__first_name",
            "user__last_name",
            "auto_renew",
            "crud_course_type__course_type",
            "created_at",
            "updated_at",
            "end_date",
        ).filter(user=self.request.user)

    def get_permissions(self):
        if self.request.method in ['PATCH', "PUT", "DELETE"]:
            self.permission_classes = (permissions.IsAdminUser,)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.CreateSubscriptionSerializer
        return super().get_serializer_class()

    def filter_queryset(self, queryset):
        status = self.request.query_params.get("status", None)
        phone = self.request.query_params.get("phone", None)

        if status:
            return queryset.filter(status=status)
        if phone:
            return queryset.filter(user__mobile_phone=phone)
        else:
            return queryset
