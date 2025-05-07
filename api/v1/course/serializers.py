from rest_framework import serializers, exceptions
from drf_spectacular.utils import extend_schema_field
from rest_framework.generics import get_object_or_404

from accounts.models import Student
from course.enums import RateChoices, StudentStatusChoices
from course.models import Course, Category, Comment, Section, SectionVideo, SectionFile, SendSectionFile, LessonCourse, \
    StudentSectionScore, PresentAbsent, StudentAccessSection, OnlineLink, SectionQuestion, AnswerQuestion, \
    CallLessonCourse, Certificate, CourseTypeModel
from subscription_app.models import Plan


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
    parent = serializers.IntegerField(required=False)
    user_name = serializers.SerializerMethodField()
    user_image = serializers.SerializerMethodField()
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.only("category_name"))
    user_is_coach = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ["id", 'comment_body', "parent", "created_at", "user_name", "user_image", "numchild", 'depth', "path",
                  "category", "user_is_coach"]
        read_only_fields = ['numchild', "depth", "path"]

    def validate(self, data):
        user = self.context['request'].user
        category_id = data['category']

        if hasattr(user, "student"):
            is_exists = LessonCourse.objects.filter(
                students__user=user,
                course__category_id=category_id
            )

        else:
            is_exists = LessonCourse.objects.filter(
                coach__user=user,
                course__category_id=category_id
            )

        if not is_exists:
            raise serializers.ValidationError({"message": "you do not permission this action"})

        return data

    def get_user_name(self, obj):
        return obj.user.get_full_name

    def get_user_image(self, obj):
        return obj.user.image.url if obj.user.image else None

    @extend_schema_field(serializers.BooleanField())
    def get_user_is_coach(self, obj):
        return obj.user.is_coach

    def create(self, validated_data):
        user = self.context['request'].user

        parent = validated_data.pop("parent", None)

        if parent:
            comment_node = get_object_or_404(Comment, pk=parent)
            return comment_node.add_child(user=user, **validated_data)
        else:
            comment = Comment.add_root(user=user, **validated_data)
        return comment


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
    course_category = serializers.SerializerMethodField()

    class Meta:
        model = LessonCourse
        fields = ["id", "course", "course_category", "progress", "coach_name", "class_name", "progress_bar"]

    def get_coach_name(self, obj):
        return obj.coach.get_coach_name

    def get_progress_bar(self, obj):
        return obj.progress_bar

    def get_course_category(self, obj):
        return obj.course.category_id


class ListCoachLessonCourseSerializer(serializers.ModelSerializer):
    course_category = serializers.SerializerMethodField()
    course_image = serializers.SerializerMethodField()

    class Meta:
        model = LessonCourse
        fields = ['id', "course", "course_category", "progress", "class_name", "course_image"]

    def get_course_category(self, obj):
        return obj.course.category_id

    def get_course_image(self, obj):
        return obj.course.course_image.url


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


class CallLessonCourseSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.filter(is_active=True).only("student_number")
    )

    class Meta:
        model = CallLessonCourse
        exclude = ('is_deleted', "deleted_at", "lesson_course")

    def create(self, validated_data):
        coach_lesson_course_pk = self.context['lesson_course_pk']
        return CallLessonCourse.objects.create(
            lesson_course_id=coach_lesson_course_pk, **validated_data
        )

    def validate(self, attrs):
        student_lesson_course = LessonCourse.objects.filter(
            students__exact=attrs["student"], id=self.context['lesson_course_pk']
        )

        if not student_lesson_course:
            raise exceptions.NotFound()

        return attrs


class HomeCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = (
            "id",
            "category_name",
            "image",
            "description"
        )



# class HomeCoursePlanSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Plan
#         fields = ("price", "plan_title")


class CourseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseTypeModel
        fields = ("course_type", "description", "price")


class HomeCourseSerializer(serializers.ModelSerializer):
    # plans = HomeCoursePlanSerializer(many=True)
    course_type_model = CourseTypeSerializer(
        many=True,
    )

    class Meta:
        model = Course
        fields = (
            "id",
            "course_name",
            "course_image",
            "course_description",
            "project_counter",
            "facilities",
            "course_level",
            "time_course",
            "course_age",
            "course_type_model",
        )


class CertificateSerializer(serializers.ModelSerializer):
    student_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = ("id", "created_at", "student_full_name")

    def get_student_full_name(self, obj):
        return obj.student.student_name if obj.student.user.first_name else None

    def create(self, validated_data):
        section_pk = self.context['section_pk']
        student_id = self.context['request'].user.student.id
        return Certificate.objects.create(student_id=student_id, section_id=section_pk, **validated_data)

    def validate(self, attrs):
        section_pk=self.context['section_pk']
        student_id = self.context['request'].user.student.id

        if Certificate.objects.filter(section_id=section_pk, student_id=student_id).exists():
            raise exceptions.ValidationError({"message": "you have already certificate"})

        return attrs


class CrudCourseTypeSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.filter(is_publish=True).only("course_name",)
    )

    class Meta:
        model = CourseTypeModel
        exclude = ("is_deleted", "deleted_at")

    def create(self, validated_data):
        course_id = self.context['home_course_pk']
        return CourseTypeModel.objects.create(course_id=course_id, **validated_data)
