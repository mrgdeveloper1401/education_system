from rest_framework import viewsets, permissions

from . import serializers
from images.models import Image


class ImageViewSet(viewsets.ModelViewSet):
    """
    search ---? ?title=title
    """
    queryset = Image.objects.defer("is_deleted", "deleted_at")
    serializer_class = serializers.ImageSerializer
    permission_classes = (permissions.IsAdminUser,)

    def filter_queryset(self, queryset):
        title = self.request.query_params.get('title', None)

        if title:
            queryset = queryset.filter(title__icontains=title)
        return queryset
