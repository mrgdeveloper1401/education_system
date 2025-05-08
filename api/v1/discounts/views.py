from rest_framework import viewsets, permissions

from discount_app.models import Discount
from . import serializers


class DiscountViewSet(viewsets.ModelViewSet):
    queryset = Discount.objects.filter(is_active=True)
    serializer_class = serializers.DiscountSerializer
    permission_classes = (permissions.IsAdminUser,)

    def get_queryset(self):
        queryset = super().get_queryset()

        content_type = self.request.query_params.get('content_type')
        object_id = self.request.query_params.get('object_id')

        if content_type and object_id:
            queryset = queryset.filter(
                content_type__model=content_type,
                object_id=object_id
            )

        return queryset
