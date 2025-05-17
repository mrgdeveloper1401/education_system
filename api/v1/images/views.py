from rest_framework import viewsets, permissions

from . import serializers
from images.models import Image


class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.only("image", "title", "file_size")
    serializer_class = serializers.ImageSerializer
    permission_classes = (permissions.IsAdminUser,)
