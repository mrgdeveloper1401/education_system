from rest_framework import viewsets, permissions, generics

from course.models import Course
from discount_app import models
from discount_app.models import Discount
from . import serializers
from ...course.paginations import CommonPagination


class CouponViewSet(viewsets.ModelViewSet):
    """
    you can use search field
    ?code=xxxx
    """
    serializer_class = serializers.CouponSerializer
    permission_classes = (permissions.IsAdminUser,)
    pagination_class = CommonPagination

    def get_queryset(self):
        query = models.Coupon.objects.defer("is_deleted", "deleted_at")

        code = self.request.query_params.get("code", None)

        if code:
            query = query.filter(code__exact=code)

        return query


class DiscountViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.DiscountSerializer
    permission_classes = (permissions.IsAdminUser,)
    queryset = Discount.objects.defer("is_deleted", "deleted_at")

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.CreateDiscountSerializer
        else:
            return super().get_serializer_class()


class DiscountCourseApiView(generics.ListAPIView):
    """
    you can use search field \n
    ?name=course_name
    """
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = serializers.DiscountCourseSerializer

    def get_queryset(self):
        query = Course.objects.filter(is_publish=True).only("course_name")
        name = self.request.query_params.get('name', None)

        if name:
            query = query.filter(course_name__contains=name)

        return query
