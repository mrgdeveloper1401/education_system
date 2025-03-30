from rest_framework import serializers, exceptions
from django.db import IntegrityError
from drf_spectacular.utils import extend_schema_field
from django.utils.translation import gettext_lazy as _

from accounts.models import Student
from course.enums import RateChoices, StudentStatusChoices
from course.models import Course, Category, Comment, Section, SectionVideo, SectionFile, SendSectionFile, LessonCourse, \
    StudentSectionScore, PresentAbsent, StudentAccessSection, OnlineLink, SectionQuestion, AnswerQuestion


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


class CoachSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ["id", "title", "description", "cover_image"]


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
        fields = ["id", "zip_file", "title", "file_type"]


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


class SimpleStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', "student_name"]


class LessonCourseSerializer(serializers.ModelSerializer):
    course = SimpleLessonCourseSerializer()
    coach_name = serializers.SerializerMethodField()
    progress_bar = serializers.SerializerMethodField()

    class Meta:
        model = LessonCourse
        fields = ["id", "course", "progress", "coach_name", "class_name", "progress_bar"]

    def get_coach_name(self, obj):
        return obj.coach.get_coach_name

    def get_progress_bar(self, obj):
        return obj.progress_bar


class ListCoachLessonCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = LessonCourse
        fields = ['id', "course", "progress", "class_name"]


class RetrieveLessonCourseSerializer(serializers.ModelSerializer):
    students = SimpleStudentSerializer(many=True)

    class Meta:
        model = LessonCourse
        fields = ['progress', "class_name", "students"]


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
        fields = ["id", "class_name", 'students']


class StudentPresentAbsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PresentAbsent
        fields = ['student_status', "created_at"]


class SendFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendSectionFile
        fields = ["id", "score", "comment_student", "zip_file", "created_at", "comment_teacher", "send_file_status",
                  "updated_at"]
        extra_kwargs = {
            "score": {"read_only": True},
            "comment_teacher": {"read_only": True},
        }

    def create(self, validated_data):
        return SendSectionFile.objects.create(
            student=self.context['request'].user.student,
            section_file_id=self.context['section_file_pk'],
            **validated_data
        )

    def validate(self, data):
        user = self.context['request'].user
        zip_file = data.get("zip_file")
        section_file_pk = self.context['section_file_pk']

        if zip_file:
            if SendSectionFile.objects.filter(section_file_id=section_file_pk, student__user=user).exists():
                raise exceptions.ValidationError({"message": "you have already file"})

        if not SectionFile.objects.filter(id=section_file_pk).exists():
            raise exceptions.NotFound()

        return data


class CoachSendFileSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.filter(is_active=True).only("student_number")
    )

    class Meta:
        model = SendSectionFile
        fields = ['score', "student", "student_name", "comment_teacher", "send_file_status"]

    def get_student_name(self, obj):
        return obj.student.student_name if obj.student else None


class OnlineLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineLink
        exclude = ['is_deleted', "deleted_at", "class_room", "updated_at"]

    def create(self, validated_data):
        coach_lesson_course_pk = self.context['coach_lesson_course_pk']
        return OnlineLink.objects.create(class_room_id=coach_lesson_course_pk, **validated_data)

    def validate(self, attrs):
        class_room_pk = self.context['coach_lesson_course_pk']
        is_publish = attrs.get('is_publish')

        if is_publish:
            if OnlineLink.objects.filter(is_publish=True, class_room_id=class_room_pk).exists():
                raise exceptions.ValidationError({"message": "you have already publish"})
        return attrs


class NestedCoachPresentAbsentSerializer(serializers.Serializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.filter(is_active=True).only("student_number", "user__first_name", "user__last_name")
    )
    section = serializers.PrimaryKeyRelatedField(
        queryset=Section.objects.filter(is_publish=True).only("id", "title")
    )
    student_status = serializers.ChoiceField(choices=StudentStatusChoices.choices, default=StudentStatusChoices.present)


class CreateCoachPresentAbsentSerializer(serializers.Serializer):
    present_absent = NestedCoachPresentAbsentSerializer(many=True)

    def create(self, validated_data):
        lst = []
        for item in validated_data['present_absent']:

            if PresentAbsent.objects.filter(section=item['section'], student=item['student']).exists():
                continue

            lst.append(
                PresentAbsent(
                    section=item['section'], student=item['student'], student_status=item['student_status']
                )
            )

        if lst:
            PresentAbsent.objects.bulk_create(lst)
        else:
            raise serializers.ValidationError({"message": "list is empty"})

        return {"present_absent": lst}


class CoachPresentAbsentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField(read_only=True)
    section_title = serializers.SerializerMethodField(read_only=True)
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.only("student_number").filter(is_active=True)
    )

    class Meta:
        model = PresentAbsent
        fields = ['id', "student", "student_status", "section", "created_at", "student_name", "section_title"]
        read_only_fields = ['section']

    def get_student_name(self, obj):
        return obj.student.student_name

    def get_section_title(self, obj):
        return obj.section.title

    def update(self, instance, validated_data):
        instance.section_id = int(self.context['section_pk'])
        return super().update(instance, validated_data)


class StudentListPresentAbsentSerializer(serializers.ModelSerializer):
    section_name = serializers.SerializerMethodField()

    class Meta:
        model = PresentAbsent
        fields = ["id", "student_status", "section_name", "created_at"]

    def get_section_name(self, obj):
        return obj.section.title


class CoachSectionFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionFile
        fields = ["id", 'zip_file', 'answer', "title", "file_type", "is_publish"]


class StudentOnlineLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineLink
        fields = ['id', "link", "created_at"]


class SectionQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionQuestion
        fields = ['id', "question_title"]


class RateAnswerSerializer(serializers.Serializer):
    rate = serializers.ChoiceField(choices=RateChoices.choices)
    section_question_id = serializers.IntegerField()


class AnswerSectionQuestionSerializer(serializers.Serializer):
    rates = RateAnswerSerializer(many=True)

    def create(self, validated_data):
        student = self.context['request'].user.student
        answers = []
        for item in validated_data['rates']:
            answer = AnswerQuestion(
                student=student,
                section_question_id=item['section_question_id'],
                rate=item['rate'],
            )
            answers.append(answer)
        created = AnswerQuestion.objects.bulk_create(answers)
        return {
            "rates": [
                {
                    "rate": i.rate,
                    "section_question_id": i.section_question_id,
                }
                for i in created
            ]
        }


class CoachStudentSendFilesSerializer(serializers.ModelSerializer):
    file_type = serializers.SerializerMethodField()
    std_name = serializers.SerializerMethodField()

    class Meta:
        model = SendSectionFile
        fields = ("student", "id", 'std_name', "zip_file", "comment_student", "file_type", "send_file_status",
                  'score', "created_at", "updated_at", "comment_teacher")

    def get_file_type(self, obj):
        return obj.section_file.file_type

    def get_std_name(self, obj):
        return obj.student.student_name


class UpdateCoachStudentSendFilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendSectionFile
        fields = ['id', "score", "comment_teacher"]


class ScoreIntoStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendSectionFile
        fields = ['score', "student", "comment_teacher"]
