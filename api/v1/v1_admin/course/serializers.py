from django.shortcuts import get_object_or_404
from rest_framework import serializers

from accounts.models import Coach
from course.models import Category, Course, Section, SectionFile, SectionVideo, CoachEnrollment, StudentEnrollment
from drf_extra_fields.fields import Base64ImageField


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
        exclude = ['is_deleted', "deleted_at"]
        read_only_fields = ['course_image']


class AdminCreateCourseSerializer(serializers.ModelSerializer):
    course_image = Base64ImageField()

    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ["category"]

    def create(self, validated_data):
        return Course.objects.create(
            category_id=self.context['category_pk'],
            **validated_data
        )


class AdminUpdateCourseSerializer(serializers.ModelSerializer):
    course_image = Base64ImageField()

    class Meta:
        model = Course
        exclude = ['is_deleted', "deleted_at", "updated_at"]


class AdminCreateCourseSectionSerializer(serializers.ModelSerializer):
    cover_image = Base64ImageField()

    class Meta:
        model = Section
        fields = ['title', "description", "is_available", "cover_image"]

    def create(self, validated_data):
        course_id = self.context['course_pk']
        return Section.objects.create(
            course_id=course_id,
            **validated_data
        )


class AdminListCourseSectionSerializer(serializers.ModelSerializer):
    cover_image = Base64ImageField()

    class Meta:
        model = Section
        exclude = ["deleted_at", "is_deleted"]


class AdminCreateCourseSectionFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionFile
        fields = ["is_publish", "zip_file", "title", "expired_data", "is_close"]

    def create(self, validated_data):
        return SectionFile.objects.create(section_id=int(self.context['section_pk']), **validated_data)


class AdminListCourseSectionFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionFile
        exclude = ['is_deleted', "deleted_at"]


class AdminCreateSectionVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionVideo
        fields = ['is_publish', "video"]

    def create(self, validated_data):
        return SectionVideo.objects.create(section_id=int(self.context['section_pk']), **validated_data)


class AdminListSectionVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionVideo
        exclude = ['is_deleted', "deleted_at"]


class AdminCourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', "course_name"]


class AdminCoachSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoachEnrollment
        fields = ["id", 'coach', "is_active"]

    def create(self, validated_data):
        course_pk = self.context['course_pk']
        return CoachEnrollment.objects.create(course_id=course_pk, **validated_data)


class AdminStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEnrollment
        fields = ['id', "student", "coach"]

    def create(self, validated_data):
        course_id = self.context['course_pk']
        return StudentEnrollment.objects.create(course_id=course_id, **validated_data)


class AdminGetStudentByCoachSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEnrollment
        fields = ["id", 'student']
