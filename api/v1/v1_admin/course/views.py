from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import exceptions

from . import serializers
from course.models import Category


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = Category.objects.only("id", "category_name")

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.CreateCategorySerializer
        if self.action in ["list", "retrieve"]:
            return serializers.ListRetrieveCategorySerializer
        if self.action in ['update', 'partial_update']:
            return serializers.UpdateCategoryNodeSerializer
        if self.action == "destroy":
            return serializers.ListRetrieveCategorySerializer
        else:
            raise exceptions.NotAcceptable
