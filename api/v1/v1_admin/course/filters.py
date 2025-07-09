from django_filters.rest_framework import FilterSet

from course.models import Comment


class AdminCommentFilter(FilterSet):
    class Meta:
        model = Comment
        fields = (
            "is_pined",
        )
