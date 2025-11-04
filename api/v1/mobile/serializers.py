from rest_framework import serializers

from course.models import Course


class ListDetailCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        exclude = (
            "is_deleted",
            "deleted_at"
        )
