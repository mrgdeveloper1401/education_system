from rest_framework import serializers, generics
from guardian.shortcuts import assign_perm

from accounts.models import Student
from course.models import Course, Category, Comment, Section, SectionVideo, SectionFile, SendSectionFile, LessonCourse, \
    StudentSectionProgress, PresentAbsent
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


class CourseSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', "title", "created_at", "cover_image"]


class CourseSectionVideoSerializer(serializers.ModelSerializer):
    section_cover_image = serializers.SerializerMethodField()

    class Meta:
        model = SectionVideo
        fields = ["id", "video", "created_at", "title", "section_cover_image"]

    def get_section_cover_image(self, obj):
        return obj.section.cover_image.url


class CourseSectionFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionFile
        fields = ['id', "zip_file", "created_at", "title", "is_close", "expired_data"]


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


class SimpleLessonCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['course_name', "course_image", "project_counter"]


class LessonCourseSerializer(serializers.ModelSerializer):
    course = SimpleLessonCourseSerializer()
    coach_name = serializers.SerializerMethodField()

    class Meta:
        model = LessonCourse
        fields = ["id", "course", "progress", "coach_name", "class_name"]

    def get_coach_name(self, obj):
        return obj.coach.get_coach_name


class SectionScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSectionProgress
        fields = ['id', "section", "score"]


class CreateUpdateSectionScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSectionProgress
        fields = ['score', "student"]

    def create(self, validated_data):
        section_pk = self.context['section_pk']
        return StudentSectionProgress.objects.create(section_id=section_pk, **validated_data)


class LessonCourseStudentSerializer(serializers.ModelSerializer):
    students = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.filter(is_active=True).only("id", "student_number"),
        many=True
    )

    class Meta:
        model = LessonCourse
        fields = ['students']

    def validate(self, attrs):
        section_pk = self.context['section_pk']

        get_section = generics.get_object_or_404(Section, pk=section_pk)

        get_student = generics.get_object_or_404(Student, id=attrs['students'])

        assign_perm("can_access_section", get_student, get_section)
        return attrs


class LessonCoursePreSentAbsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PresentAbsent
        exclude = ['is_deleted', "deleted_at", "created_at", "updated_at"]

    def create(self, validated_data):
        lesson_course_id = self.context['lesson_course_pk']
        return PresentAbsent.objects.create(lesson_course_id=lesson_course_id, **validated_data)
