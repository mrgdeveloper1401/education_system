from rest_framework import viewsets, mixins

from . import serializers
from order_app.models import Order, CourseSignUp


class OrderViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = serializers.OrderSerializer
    queryset = Order.objects.only("course", "price", "mobile_phone")


class CourseSignupViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = serializers.CourseSignUpSerializer
    queryset = CourseSignUp.objects.only(
        "course__course_name",
        "fist_name",
        "last_name",
        "mobile_phone"
    )
