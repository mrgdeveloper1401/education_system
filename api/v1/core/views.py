from rest_framework import viewsets, permissions

from . import serializers
from core.models import SitemapEntry

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
