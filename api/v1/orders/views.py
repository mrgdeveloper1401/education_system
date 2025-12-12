
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework.views import APIView

from . import serializers
from order_app.models import Order


class OrderViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = serializers.OrderSerializer
    queryset = Order.objects.only("course", "price", "mobile_phone")


class CourseSignupView(APIView):
    """
    referral_code can be sent null data
    """
    serializer_class = serializers.CourseSignUpSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_201_CREATED)


# class PaymentViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
#     permission_classes = (permissions.IsAuthenticated,)
#     serializer_class = serializers.PaymentSerializer
#
#     def get_queryset(self):
#         return Payment.objects.filter(user=self.request.user).defer(
#             "is_deleted",
#             "deleted_at"
#         )
