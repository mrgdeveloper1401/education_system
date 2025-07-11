from rest_framework import viewsets, permissions

from . import serializers
from core.models import SitemapEntry, CourseSiteInformation

class SitemapViewSet(viewsets.ModelViewSet):
    queryset = SitemapEntry.objects.only(
        "slug_text",
        "last_modified",
        "changefreq",
        "priority",
    )
    serializer_class = serializers.SiteMapSerializer

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            self.permission_classes = (permissions.IsAdminUser,)
        return super().get_permissions()


class CourseSiteInformationViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CourseSiteInformationSerializer
    queryset = CourseSiteInformation.objects.defer(
        "is_deleted",
        "deleted_at",
        "updated_at",
        "created_at"
    )

    def get_permissions(self):
        if self.action in ("create", "update", "partial_update", "destroy"):
            self.permission_classes = (permissions.IsAdminUser,)
        return super().get_permissions()
