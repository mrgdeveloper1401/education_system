from rest_framework import serializers
from course.models import Course, Category, Comment, Section, SectionVideo, SectionFile, SendSectionFile, LessonCourse, \
    CoachAccessCourse, StudentAccessCourse
from drf_spectacular.utils import extend_schema_field
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CategoryTreeNodeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_children(self, obj):
        return CategoryTreeNodeSerializer(obj.get_children(), many=True).data

    class Meta:
        model = Category
        exclude = ['created_at', "updated_at", "deleted_at", "is_deleted"]


class CategoryNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', "category_name"]


class DestroyCategoryNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_name']

    def to_representation(self, instance):
        return "successfully destroy category"


class CourseSerializer(serializers.ModelSerializer):
    category = serializers.CharField(read_only=True)

    class Meta:
        model = Course
        exclude = ['deleted_at', "is_deleted", "created_at", "updated_at"]

    def create(self, validated_data):
        category_pk = self.context["category_pk"]
        course = Course.objects.create(category_id=category_pk, **validated_data)
        return course


class ListCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', "course_name", "course_image", "course_price", "course_duration"]


class RetrieveCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['course_name', "course_description", "course_duration", "course_price"]


class ListSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', "title", "course", "created_at", "cover_image"]


class RetrieveSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['course', "title", "description", "cover_image"]


class ListSectionVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionVideo
        fields = ["id", "video", "created_at"]


class RetrieveSectionVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionVideo
        fields = ['video']


class ListSectionFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionFile
        fields = ['id', "zip_file", "created_at", "title", "is_close"]


class RetrieveSectionFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionFile
        fields = ['zip_file', "expired_data"]


class CommentSerializer(serializers.ModelSerializer):
    student = serializers.CharField(read_only=True)

    class Meta:
        model = Comment
        exclude = ['is_deleted', "deleted_at", "user", "is_publish", "updated_at", "course"]
        extra_kwargs = {
            "is_publish": {'read_only': True},
        }

    def create(self, validated_data):
        user = self.context['user']
        course_pk = self.context['course_pk']
        return Comment.objects.create(course_id=course_pk, user=user, **validated_data)


class SendSectionFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendSectionFile
        fields = ["id", 'zip_file']

    def validate(self, attrs):
        section_file = self.context['section_file_pk']
        section_id = self.context['section_pk']
        get_section_file = SectionFile.objects.filter(id=section_file).first()
        if get_section_file.expired_data < timezone.now() or get_section_file.is_close:
            raise serializers.ValidationError({"message": _("this section_file is close or expired")})
        if not SectionFile.objects.filter(id=self.context['section_file_pk'], section_id=section_id).exists():
            raise serializers.ValidationError({"message": _("this section_file is not exist")})
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user.student
        section_file_id = self.context['section_file_pk']
        return SendSectionFile.objects.create(student=user, section_file_id=section_file_id, **validated_data)


class NestedCourseSectionFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionFile
        fields = ['zip_file']


class NestedCourseSectionVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionVideo
        fields = ['video']


class NestedCourseSectionSerializer(serializers.ModelSerializer):
    section_videos = NestedCourseSectionVideoSerializer(many=True)
    section_files = NestedCourseSectionFileSerializer(many=True)

    class Meta:
        model = Section
        fields = ['title', "section_videos", "section_files"]


class NestCourseSerializer(serializers.ModelSerializer):
    sections = NestedCourseSectionSerializer(many=True)

    class Meta:
        model = Course
        fields = ["sections"]


class LessonTakenByCoachSerializer(serializers.ModelSerializer):
    course_image = serializers.SerializerMethodField()
    coach = serializers.CharField(source="coach.get_coach_name")
    course = NestCourseSerializer()

    class Meta:
        model = LessonCourse
        fields = ['class_name', "coach", "course_image", "course", "created_at", "progress"]

    def get_course_image(self, obj):
        return obj.course.course_image.url if obj.course.course_image else None


class LessonTakenByStudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = LessonCourse
        fields = ['course', "coach", "progress"]
