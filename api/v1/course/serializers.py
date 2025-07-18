from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers, exceptions
from drf_spectacular.utils import extend_schema_field
from rest_framework.generics import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from accounts.models import Student, PrivateNotification
from course.enums import RateChoices, StudentStatusChoices
from course.models import Course, Category, Comment, Section, SectionVideo, SectionFile, SendSectionFile, LessonCourse, \
    StudentSectionScore, PresentAbsent, StudentAccessSection, OnlineLink, SectionQuestion, AnswerQuestion, \
    CallLessonCourse, Certificate, CourseTypeModel, StudentEnrollment, CertificateTemplate
from discount_app.models import Discount
from course.tasks import create_qr_code, admin_user_request_certificate, send_notification_when_score_is_accepted


class CategoryTreeNodeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    @extend_schema_field(serializers.ListField(child=serializers.DictField()))
    def get_children(self, obj):
        return CategoryTreeNodeSerializer(obj.get_children(), many=True).data

    class Meta:
        model = Category
        exclude = ('created_at', "updated_at", "deleted_at", "is_deleted")


class CourseSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('id', "title", "cover_image")


class StudentAccessSectionSerializer(serializers.ModelSerializer):
    section = CourseSectionSerializer()

    class Meta:
        model = StudentAccessSection
        fields = ('section', "is_access")


class CoachSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ("id", "title", "description", "cover_image")


class CourseSectionDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ('title', "cover_image", "description", "created_at")


class StudentAccessSectionDetailSerializer(serializers.ModelSerializer):
    section = CourseSectionDetailSerializer()

    class Meta:
        model = StudentAccessSection
        fields = ('section', "is_access")


class CourseSectionVideoSerializer(serializers.ModelSerializer):
    section_cover_image = serializers.SerializerMethodField()

    class Meta:
        model = SectionVideo
        fields = ("id", "video", "video_url", "title", "section_cover_image")

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
        fields = ("id",
                  'comment_body',
                  "parent",
                  "created_at",
                  "user_name",
                  "user_image",
                  "numchild",
                  'depth',
                  "path",
                  "category",
                  "user_is_coach",
                  "is_pined"
                  )
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
        fields = ('id', "student_name")


class LessonCourseSerializer(serializers.ModelSerializer):
    course = SimpleLessonCourseSerializer()
    coach_name = serializers.SerializerMethodField()
    progress_bar = serializers.SerializerMethodField()
    course_category = serializers.SerializerMethodField()

    class Meta:
        model = LessonCourse
        fields = ("id", "course", "course_category", "progress", "coach_name", "class_name", "progress_bar")

    def get_coach_name(self, obj):
        return obj.coach.get_coach_name

    def get_progress_bar(self, obj):
        # تعداد سکشن‌هایی که دانشجو نمره بالای 60 گرفته
        passed_sections = StudentSectionScore.objects.filter(
            student__user_id=self.context['request'].user.id,
            section__course__lesson_course=obj,
            score__gte=60
        ).count()

        # تعداد کل سکشن‌های این دوره
        total_sections = Section.objects.filter(
            course__lesson_course=obj,
            is_publish=True
        ).count()

        # محاسبه درصد پیشرفت
        if total_sections > 0:
            progress_percentage = (passed_sections / total_sections) * 100
            return round(progress_percentage, 2)  # گرد کردن به دو رقم اعشار
        return 0

    def get_course_category(self, obj):
        return obj.course.category_id


class ListCoachLessonCourseSerializer(serializers.ModelSerializer):
    course_category = serializers.SerializerMethodField()
    course_image = serializers.SerializerMethodField()

    class Meta:
        model = LessonCourse
        fields = ('id', "course", "course_category", "progress", "class_name", "course_image")

    def get_course_category(self, obj):
        return obj.course.category_id

    def get_course_image(self, obj):
        return obj.course.course_image.url if obj.course.course_image else None


class SectionScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentSectionScore
        fields = ("score",)


class StudentLessonCourseSerializer(serializers.ModelSerializer):
    student_phone = serializers.SerializerMethodField()
    student_second_number = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentEnrollment
        fields = ("id", "student_status", "student_name", "student_phone", "student_second_number")

    def get_student_phone(self, obj):
        return obj.student.user.mobile_phone

    def get_student_second_number(self, obj):
        return obj.student.user.second_mobile_phone

    def get_student_name(self, obj):
        return obj.student.student_name


class StudentPresentAbsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PresentAbsent
        fields = ('student_status', "created_at")


class SendFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendSectionFile
        fields = ("id", "score", "comment_student", "zip_file", "created_at", "comment_teacher", "send_file_status",
                  "updated_at")
        extra_kwargs = {
            "score": {"read_only": True},
            "comment_teacher": {"read_only": True},
            "send_file_status": {"read_only": True}
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
        fields = ("id", "student_status", "section_name", "created_at")

    def get_section_name(self, obj):
        return obj.section.title


class CoachSectionFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionFile
        fields = ("id", 'zip_file', 'answer', "title", "file_type", "is_publish")


class StudentOnlineLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = OnlineLink
        fields = ('id', "link", "created_at")


class SectionQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionQuestion
        fields = ('id', "question_title")


class RateAnswerSerializer(serializers.Serializer):
    rate = serializers.ChoiceField(choices=RateChoices.choices)
    section_question_id = serializers.IntegerField()


class AnswerSectionQuestionSerializer(serializers.Serializer):
    rates = RateAnswerSerializer(many=True)

    def create(self, validated_data):
        user_id = self.context['request'].user.id # get user_id by context
        student = Student.objects.filter(user_id=user_id).only("student_number") # filter query student

        # check user is student
        if not student.exists():
            raise exceptions.ValidationError(
                {
                    "message": _("your account not student")
                }
            )

        student = student.first()

        answers = []

        for item in validated_data['rates']:
            answer = AnswerQuestion(
                student=student,
                section_question_id=item['section_question_id'],
                rate=item['rate'],
            )
            answers.append(answer)

        if answers:
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

        # print(answers)
        return {"rates": []}


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
        fields = ('id', "score", "comment_teacher")

    def update(self, instance, validated_data):
        data = super().update(instance, validated_data)

        lesson_course_pk = self.context['lesson_course_pk']
        section_pk = self.context['section_pk']
        user_id = self.context['user_id']
        student_send_files_pk = self.context['student_send_files_pk']

        send_notification_when_score_is_accepted.delay(
            lesson_course_id=lesson_course_pk,
            section_file_pk=student_send_files_pk,
            section_pk=section_pk,
            score=instance.score,
            user_id=user_id
        )
        return data


class ScoreIntoStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = SendSectionFile
        fields = ('score', "student", "comment_teacher")


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
            "description",
            "description_slug"
        )


class CourseTypeSerializer(serializers.ModelSerializer):
    discounts = serializers.SerializerMethodField()

    class Meta:
        model = CourseTypeModel
        fields = ("id", "course_type", "description", "price", "discounts", "plan_type", "amount")

    def get_discounts(self, obj):
        discounts = Discount.objects.filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).values("id", "percent", "start_date", "end_date")
        return discounts


class HomeCourseSerializer(serializers.ModelSerializer):
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
            "description_slug"
        )


class CertificateSerializer(serializers.ModelSerializer):
    # student_full_name = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        fields = ("id", "final_pdf")
        read_only_fields = ("final_pdf",)

    # def get_student_full_name(self, obj):
    #     return obj.student.student_name if obj.student.user.first_name else None

    def create(self, validated_data):
        section_pk = self.context['section_pk']
        lesson_course_pk = self.context["lesson_course_pk"]
        user_id = self.context['request'].user.id # get user_id by context serializer
        student = Student.objects.filter(user_id=user_id).select_related(
            "user"
        ).only(
            "student_number",
            "user__first_name",
            "user__last_name",
        ) # queryset student

        # check dose exists student
        if not student.exists():
            raise exceptions.ValidationError(
                {
                    "message": _("student not found")
                }
            )

        # get object student id
        student = student.first()

        # check certificate dose already exists?
        certificate = Certificate.objects.filter(
            section_id=section_pk,
            student_id=student.id,
        ).only("id")

        if self.instance is None and certificate.exists():
            raise exceptions.ValidationError(
                {
                    "message": _("you have already certificate")
                }
            )

        # create request certificate
        certificate = Certificate.objects.create(
            student_id=student.id,
            section_id=section_pk,
            **validated_data
        )
        # call celery task celery
        create_qr_code.delay(
            information = {
                "unique_code_certificate": certificate.unique_code,
                "student_number": student.student_number,
                "student_name": student.student_name,
                "section_id": section_pk,
                "lesson_course_pk": lesson_course_pk
            },
            certificate_id = {
                "id": certificate.id
            }
        )
        # create notification for admin , task celery
        admin_user_request_certificate.delay(
            # url_id = {
            #     f"/api_course/student_lesson_course/{lesson_course_pk}/sections/{section_pk}/certificate/"
            # }
            body=f"ادمین محترم کاربر {certificate.student.student_name} \n"
                 f"درخواست گواهی نامه داده هست",
            link=f"lesson_course_id:{lesson_course_pk}/section_id:{section_pk}/"
        )
        return certificate

    def validate(self, attrs):
        section_pk=self.context['section_pk']
        user_id=self.context['request'].user.id

        # get section_score
        section_score = StudentSectionScore.objects.filter(
            section_id=section_pk,
            student__user_id=user_id,
            score__gte=60
        ).only(
            "id"
        )

        if section_score:
            # check student access section
            student_access_section = StudentAccessSection.objects.filter(
                section_id=section_pk,
                student__user_id=self.context['request'].user.id,
                section__is_last_section=True,
                section__is_publish=True,
                is_access=True
            ).only(
                "id"
            )

            if not student_access_section.exists():
                raise exceptions.ValidationError(
                    {
                        "message": _("you not arrived last_section or this section not last_section")
                    }
                )
        else:
            raise exceptions.ValidationError(
                {
                    "message": _("this section you have not been accept or this section not last_section")
                }
            )
        return attrs


# class CertificateTemplateSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = CertificateTemplate
#         fields = (
#             "id",
#             "template_image",
#             "is_active"
#         )
#
#     def to_representation(self, instance):
#         data = super().to_representation(instance)
#
#         user_is_staff = self.context['request'].user.is_staff
#         if user_is_staff is False:
#              data.pop("is_active", None)
#
#         return data


class CrudCourseTypeSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.filter(is_publish=True).only("course_name",)
    )
    discounts = serializers.SerializerMethodField()

    class Meta:
        model = CourseTypeModel
        exclude = ("is_deleted", "deleted_at")

    def create(self, validated_data):
        course_id = self.context['course_pk']
        return CourseTypeModel.objects.create(course_id=course_id, **validated_data)

    def get_discounts(self, obj):
        discounts = Discount.objects.filter(
            content_type=ContentType.objects.get_for_model(obj),
            object_id=obj.id,
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now(),
        ).values("id", "percent", "start_date", "end_date")
        return discounts


class AllCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            "id",
            "course_name",
            "course_description",
            "course_image",
            "project_counter",
            "facilities",
            "course_level",
            "time_course",
            "course_age",
            "description_slug"
        )


class SendNotificationUserSendSectionFile(serializers.Serializer):
    lesson_course = serializers.PrimaryKeyRelatedField(
        queryset=LessonCourse.objects.only("class_name", "is_active").filter(is_active=True),
    )
    section = serializers.PrimaryKeyRelatedField(
        queryset=Section.objects.only("title").filter(is_publish=True)
    )

    def validate(self, attrs):
        student = Student.objects.filter(user=self.context['request'].user).only("student_number")

        if not student:
            raise exceptions.ValidationError({"message": "user has no student"})
        return attrs

    def create(self, validated_data):
        lesson_course = validated_data['lesson_course']
        coach = lesson_course.coach
        coach_user = coach.user
        course = lesson_course.course
        section_id = validated_data['section'].id
        user = self.context['request'].user
        user_full_name = user.get_full_name

        return PrivateNotification.objects.create(
            user=coach_user,
            title="notification send section file",
            body=f"کاربر {user_full_name} تمرینی را ارسال کرده هست ",
            notification_type="send_section_file",
            char_link=f"lesson_course_id{lesson_course}/section_id:{section_id}/course_id:{course.id}/"
        )

    def to_representation(self, instance):
        res = "notification created"
        return {
            "message": res
        }


class ListCourseIdTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = (
            "id",
            "course_name"
        )


class CertificateValidateSerializer(serializers.Serializer):
    uuid_field = serializers.UUIDField()
