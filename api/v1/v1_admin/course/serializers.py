from django.shortcuts import get_object_or_404
from rest_framework import serializers

from course.models import Category, Course
from images.models import Image


class CreateCategorySerializer(serializers.ModelSerializer):
    parent = serializers.IntegerField(required=False)

    class Meta:
        model = Category
        fields = ['category_name', 'parent']

    def create(self, validated_data):
        parent = validated_data.pop("parent", None)
        if parent is None:
            instance = Category.add_root(**validated_data)
        else:
            category = get_object_or_404(Category, pk=parent)
            instance = category.add_child(**validated_data)
        return instance


class ListRetrieveCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["id", 'category_name']


class UpdateCategoryNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_name']


class AdminListCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', "course_name", "course_image"]
        read_only_fields = ['course_image']


class AdminCreateCourseSerializer(serializers.ModelSerializer):
    # course_image = serializers.ImageField()

    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ["category"]

    def create(self, validated_data):
        category_id = self.context['category_pk']
        # course_image = validated_data.pop("course_image")
        # if course_image:
        #     image = Image.objects.create(image=course_image)
        return Course.objects.create(
            category_id=category_id,
            # course_image=image,
            **validated_data
        )


class AdminUpdateCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        exclude = ['is_deleted', "deleted_at"]
        read_only_fields = ["course_image"]
