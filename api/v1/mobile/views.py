from rest_framework import mixins, viewsets, permissions, generics

from . import serializers
from course.models import Course, Category


class ListDetailCourseView(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.ListDetailCourseSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Course.objects.filter(
            is_publish=True
        ).defer(
            "is_deleted",
            "deleted_at"
        ).select_related(
            "category"
        )

    def filter_queryset(self, queryset):
        category_id = self.request.query_params.get("category_id", None)
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset


class ListCategoryView(generics.ListAPIView):
    serializer_class = serializers.ListCategorySerializer
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Category.objects.filter(
        is_publish=True
    ).only(
        "category_name",
    )
