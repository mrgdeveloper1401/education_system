from rest_framework import mixins, viewsets, permissions

from . import serializers
from course.models import Course


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
