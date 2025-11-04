from rest_framework import serializers

from course.models import Course, Category


class ListDetailCourseSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.category_name", read_only=True)

    class Meta:
        model = Course
        exclude = (
            "is_deleted",
            "deleted_at"
        )


class ListCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "category_name",
        )
