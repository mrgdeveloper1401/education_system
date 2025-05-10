from rest_framework import viewsets, mixins, permissions

from utils.permissions import NotAuthenticate
from . import serializers
from order_app.models import Order, CourseSignUp, Payment


class OrderViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = serializers.OrderSerializer
    queryset = Order.objects.only("course", "price", "mobile_phone")


class CourseSignupViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = serializers.CourseSignUpSerializer
    queryset = CourseSignUp.objects.only(
        "course__course_name",
        "fist_name",
        "last_name",
        "mobile_phone",
        "have_account"
    )


# class PaymentViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
#     permission_classes = (permissions.IsAuthenticated,)
#     serializer_class = serializers.PaymentSerializer
#
#     def get_queryset(self):
#         return Payment.objects.filter(user=self.request.user).defer(
#             "is_deleted",
#             "deleted_at"
#         )
