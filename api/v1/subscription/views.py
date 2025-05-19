from django.conf import settings
from rest_framework import viewsets, permissions, mixins, views, response, status

from subscription_app.models import Subscription, PaymentSubscription, PaymentVerify
from utils.gateway import BitPay, Zibal
from . import serializers
# from .serializers import VerifyPaymentSerializer
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
        if self.request.method in ('PATCH', "PUT", "DELETE"):
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


class PaymentSubscriptionViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    pagination --> 20 item
    user send request and get token for gateway
    access --> admin
    """
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.PaymentSubscriptionSerializer
    pagination_class = CommonPagination

    def get_queryset(self):
        return PaymentSubscription.objects.filter(subscription__user=self.request.user).only(
            "subscription__user",
            "subscription__price",
            "subscription__end_date",
            "subscription__status",
            "subscription__course_id",
            "created_at",
            "response_payment"
        ).select_related("subscription")


class PayApiView(views.APIView):
    """
    this api user, click button pay and create payment_subscription
    """
    serializer_class = serializers.PaySubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        ser = self.serializer_class(data=request.data, context={'request': request})
        ser.is_valid(raise_exception=True)
        ser.save()
        return response.Response(ser.data, status=status.HTTP_201_CREATED)


class VerifyPaymentView(views.APIView):
    """
    verify payment
    """
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        zibal = Zibal(
            api_key=settings.ZIBAL_MERCHENT_ID,
            call_back_url=settings.ZIBAL_CALLBACK_URL
        )
        zibal_verify = zibal.verify(kwargs)
        PaymentVerify.objects.create(verify_payment=zibal, user=request.user)
        return response.Response({"zibal_verify": zibal_verify}, status=status.HTTP_200_OK)


class PaymentVerifyView(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.PaymentVerifySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return PaymentVerify.objects.filter(user=self.request.user).only(
            "created_at",
            "verify_payment"
        )
