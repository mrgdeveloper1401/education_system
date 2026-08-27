from django_filters.rest_framework import FilterSet

from apps.course_app.models import Comment


class AdminCommentFilter(FilterSet):
    class Meta:
        model = Comment
        fields = (
            "is_pined",
        )
