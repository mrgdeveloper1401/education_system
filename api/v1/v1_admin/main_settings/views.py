from rest_framework import viewsets, permissions

from main_settings.models import Banner
from . import serializers
from ...course.paginations import CommonPagination


class BannerViewSet(viewsets.ModelViewSet):
    queryset = Banner.objects.defer("is_deleted", "deleted_at")
    serializer_class = serializers.BannerSerializer
    pagination_class = CommonPagination

    def get_permissions(self):
        if not self.request.method in permissions.SAFE_METHODS:
            self.permission_classes = (permissions.IsAdminUser,)
        return super().get_permissions()
