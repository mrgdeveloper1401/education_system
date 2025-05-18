from django.conf import settings
from rest_framework import viewsets, permissions, mixins, views, response, status

from subscription_app.models import Subscription, PaymentSubscription
from utils.gateway import BitPay
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
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = serializers.PaymentSubscriptionSerializer

    def get_queryset(self):
        return PaymentSubscription.objects.filter(subscription__user=self.request.user).only(
            "subscription__user",
            "subscription__price",
            "subscription__end_date",
            "subscription__status",
            "subscription__course_id",
            "created_at",
            "response_payment"
        )


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
    # permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        bit_pay = BitPay(
            api_key=settings.BITPAY_MERCHANT_ID
        )
        bit_pay_verify = bit_pay.verify(
            trans_id=request.query_params.get('trans_id'),
            id_get=request.query_params.get('id_get'),
        )
        return response.Response({
            "bit_pay_verify": bit_pay_verify,
            "trans_id": request.query_params.get('trans_id'),
            "id_get": request.query_params.get("id_get")
        }, status=status.HTTP_200_OK)
