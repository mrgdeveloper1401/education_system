from rest_framework import serializers, exceptions

from accounts.models import Student
from course.models import Course, Category, Comment, Section, SectionVideo, SectionFile, SendSectionFile, LessonCourse, \
    StudentSectionScore, PresentAbsent, StudentAccessSection, OnlineLink
from drf_spectacular.utils import extend_schema_field


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
        fields = ['id', "title", "cover_image"]


class StudentAccessSectionSerializer(serializers.ModelSerializer):
    section = CourseSectionSerializer()

    class Meta:
        model = StudentAccessSection
        fields = ['section', "is_access"]


class CoachAccessSectionSerializer(serializers.ModelSerializer):
    section = CourseSectionSerializer()

    class Meta:
        model = StudentAccessSection
        fields = ["id", "section", "is_access", "student"]


class CourseSectionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['title', "cover_image", "description", "created_at"]


class StudentAccessSectionDetailSerializer(serializers.ModelSerializer):
    section = CourseSectionDetailSerializer()

    class Meta:
        model = StudentAccessSection
        fields = ['section', "is_access"]


class CourseSectionVideoSerializer(serializers.ModelSerializer):
    section_cover_image = serializers.SerializerMethodField()

    class Meta:
        model = SectionVideo
        fields = ["id", "video", "title", "section_cover_image"]

    def get_section_cover_image(self, obj):
        return obj.section.cover_image.url


class CourseSectionFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionFile
        fields = ["id", "zip_file", "title"]


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
        model = StudentSectionScore
        fields = ["score"]


class StudentNameLessonCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', "student_name", "student_number"]


class StudentLessonCourseSerializer(serializers.ModelSerializer):
    students = StudentNameLessonCourseSerializer(many=True)

    class Meta:
        model = LessonCourse
        fields = ["class_name", 'students']


class StudentPresentAbsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PresentAbsent
        fields = ['is_present']


class SendFileSerializer(serializers.ModelSerializer):
    section_file = serializers.PrimaryKeyRelatedField(
        queryset=SectionFile.objects.filter(is_publish=True).only("id", "is_publish", "section_id")
    )

    class Meta:
        model = SendSectionFile
        fields = ["id", 'section_file', "score", "description", "zip_file"]
        extra_kwargs = {
            "score": {"read_only": True},
        }

    def create(self, validated_data):
        return SendSectionFile.objects.create(student=self.context['request'].user.student, **validated_data)

    def validate(self, data):
        user = self.context['request'].user
        section_file = data.get("section_file")

        if section_file:
            if SendSectionFile.objects.filter(section_file_id=data['section_file'], student__user=user).exists():
                raise exceptions.ValidationError({"message": "you have already file"})
        return data


class CoachSectionScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSectionScore
        fields = ['id', "score", "student"]


class OnlineLinkSerializer(serializers.ModelSerializer):
    class_room = serializers.PrimaryKeyRelatedField(
        queryset=LessonCourse.objects.filter(is_active=True)
    )

    class Meta:
        model = OnlineLink
        exclude = ['is_deleted', "deleted_at"]
