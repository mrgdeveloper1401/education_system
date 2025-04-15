from rest_framework import viewsets, permissions

from discount_app import models
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
