from rest_framework import serializers

from course.models import Course


class ListDetailCourseSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.category_name", read_only=True)

    class Meta:
        model = Course
        exclude = (
            "is_deleted",
            "deleted_at"
        )
