from django.conf import settings
from rest_framework import viewsets, permissions, mixins, views, response, status, generics, exceptions

from subscription_app.models import Subscription, PaymentSubscription, PaymentVerify
from utils.gateway import BitPay, Zibal
from . import serializers
# from .serializers import VerifyPaymentSerializer
from ..course.paginations import CommonPagination


class SubscriptionViewSet(viewsets.ModelViewSet):
    """
    status --> active / expired / pending / canceled / trial \n
    pagination --> 20 item \n
    search --> ?status=status   | ?phone=mobile_phone \n
    description --> if user is amin return all query else return owner query
    """
    serializer_class = serializers.SubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CommonPagination

    def get_queryset(self):
        query = Subscription.objects.select_related(
            "user",
            "course__category",
            "coupon",
            "crud_course_type"
        ).only(
            "course__course_name",
            "course__category__category_name",
            "user__first_name",
            "user__last_name",
            "coupon__code",
            "created_at",
            "updated_at",
            "status",
            "price",
            "crud_course_type__course_type",
            "auto_renew",
            "end_date",
            "user__mobile_phone"
        )
        if self.request.user.is_staff is False:
            query = query.filter(user=self.request.user)
        return query

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

        if status and phone:
            queryset = queryset.filter(status=status, phone__icontains=phone)
        elif status:
            queryset = queryset.filter(status=status)
        elif phone:
            queryset = queryset.filter(user__mobile_phone=phone)
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


class PayApiView(generics.CreateAPIView):
    """
    this api user, click button pay and create payment_subscription
    """
    serializer_class = serializers.PaySubscriptionSerializer
    permission_classes = (permissions.IsAuthenticated,)


class VerifyPaymentView(views.APIView):
    """
    verify payment \n
    you must send data as query params --> ?status=status&trackId=trackId
    """
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        track_id = request.query_params.get('trackId')

        if not track_id:
            raise exceptions.ValidationError({"message": "please enter query params success and track_id and status"})

        zibal = Zibal(
            api_key=settings.ZIBAL_MERCHENT_ID,
            call_back_url=settings.ZIBAL_CALLBACK_URL
        )
        zibal_verify = zibal.verify(track_id=track_id)
        PaymentVerify.objects.create(verify_payment=zibal_verify, user=request.user)
        payment_subscription = PaymentSubscription.objects.filter(response_payment__trackId=int(track_id)).only(
            "response_payment"
        )

        if not payment_subscription.exists():
            raise exceptions.ValidationError({"message": "track id dose not exits"})

        get_payment_subscription = payment_subscription.last()
        status_response = zibal_verify.get("success", None)

        if int(status_response) == 1:
            get_payment_subscription.subscription.status='active'
            get_payment_subscription.subscription.save()

        return response.Response({"zibal_verify": zibal_verify}, status=status.HTTP_200_OK)


class PaymentVerifyView(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.PaymentVerifySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return PaymentVerify.objects.filter(
            user=self.request.user
        ).only(
            "created_at",
            "verify_payment"
        )
