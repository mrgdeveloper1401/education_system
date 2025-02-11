from rest_framework import exceptions

from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from images.models import Image

from . import serializers
from .pagination import AdminImagePagination


class ImageViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    pagination_class = AdminImagePagination

    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.AdminCreateUpdateImageSerializer
        if self.action in ['update', 'partial_update', "retrieve", "destroy"]:
            return serializers.AdminImageUpdateRetrieveSerializer
        if self.action == "list":
            return serializers.AdminImageListSerializer
        else:
            raise exceptions.NotAcceptable()

    def get_queryset(self):
        if self.action == "list":
            queryset = Image.objects.all().only("id", "title", "image", "width", "height")
        else:
            queryset = Image.objects.all()
        return queryset
