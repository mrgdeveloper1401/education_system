from django.db.models.signals import post_save
from django.shortcuts import get_object_or_404
from rest_framework import serializers, exceptions
from django.utils.translation import gettext_lazy as _

from accounts.models import Student, Otp, Coach
from course.enums import StudentStatusEnum
from course.models import Category, Course, Section, SectionFile, SectionVideo, LessonCourse, Certificate, \
    PresentAbsent, SectionQuestion, AnswerQuestion, Comment, SignupCourse, StudentEnrollment, StudentAccessSection


class CreateCategorySerializer(serializers.ModelSerializer):
    parent = serializers.IntegerField(required=False)

    class Meta:
        model = Category
        fields = ('category_name', 'parent', "image", "description", "description_slug")

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
        fields = ("id", 'category_name', "image", "description", "description_slug")


class UpdateCategoryNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('category_name', "image", "description", "description_slug")


class AdminCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        exclude = ('is_deleted', "deleted_at", "category")
        extra_kwargs = {
            "facilities": {
                "required": False
            }
        }

    def create(self, validated_data):
        return Course.objects.create(category_id=self.context['category_pk'],**validated_data)


class AdminCreateCourseSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        exclude = ("is_deleted", "deleted_at", "course")
        read_only_fields = ("course",)

    def validate(self, attrs):
        # get course by context
        course_id = self.context['course_pk']

        try:
            course = Course.objects.filter(id=course_id).only("course_name")
        except Course.DoesNotExist:
            raise exceptions.ValidationError("Course does not exist")

        # get all section and filter is_last_section
        course_sections_is_last = course.first().sections.filter(is_last_section=True, is_publish=True).only(
            "course_id"
        )

        # check is_last_section dose it exists or not?
        if course_sections_is_last:
            raise exceptions.ValidationError("you have already is_last_section")

        return attrs

    def create(self, validated_data):
        course_id = self.context['course_pk']
        return Section.objects.create(course_id=course_id,**validated_data)


class AdminCourseSectionFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = SectionFile
        fields = ("id", "is_publish", "zip_file", "title", "file_type", "answer", "created_at", "updated_at")

    def create(self, validated_data):
        return SectionFile.objects.create(section_id=int(self.context['section_pk']), **validated_data)


class AdminListCourseSectionFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionFile
        exclude = ('is_deleted', "deleted_at")


class AdminSectionVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionVideo
        exclude = ('is_deleted', "deleted_at", "section")

    def create(self, validated_data):
        return SectionVideo.objects.create(section_id=int(self.context['section_pk']), **validated_data)


class AdminCourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ('id', "course_name")


class AdminLessonCourseSerializer(serializers.ModelSerializer):
    coach = serializers.PrimaryKeyRelatedField(
        queryset=Coach.objects.only("coach_number")
    )
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.only("course_name")
    )

    class Meta:
        model = LessonCourse
        exclude = ('is_deleted', "deleted_at")

    def create(self, validated_data):
        return LessonCourse.objects.create(**validated_data)
        # class_room = LessonCourse.objects.create(**validated_data)

        # if students:
        #     lst = [
        #         StudentEnrollment(
        #             student=i,
        #             lesson_course=class_room
        #         )
        #         for i in students
        #     ]
        #     StudentEnrollment.objects.bulk_create(lst)
        # return class_room


class AdminStudentPresentAbsentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    section_name = serializers.SerializerMethodField()

    class Meta:
        model = PresentAbsent
        fields = ('id', "student_status", "student_name", "section_name", "created_at")

    def get_student_name(self, obj):
        return obj.student.student_name

    def get_section_name(self, obj):
        return obj.section.title


class AdminSectionQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionQuestion
        fields = ('id', "question_title", "is_publish", "created_at")

    def create(self, validated_data):
        section_pk = self.context['section_pk']
        return SectionQuestion.objects.create(section_id=section_pk, **validated_data)


class AnswerQuestionSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.only("student_number"))

    class Meta:
        model = AnswerQuestion
        fields = ('id', "student", "created_at", "rate")


class AdminCoachRankingSerializer(serializers.ModelSerializer):
    question_title = serializers.SerializerMethodField()
    student_name = serializers.SerializerMethodField()
    section_name = serializers.SerializerMethodField()

    class Meta:
        model = AnswerQuestion
        fields = ['rate', "question_title", "student_name", "section_name", 'section_question']

    def get_question_title(self, obj):
        return obj.section_question.question_title

    def get_student_name(self, obj):
        return obj.student.student_name

    def get_section_name(self, obj):
        return obj.section_question.section.title


class AdminCommentSerializer(serializers.ModelSerializer):
    parent = serializers.IntegerField(required=False)
    user_name = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        exclude = ("is_deleted", "deleted_at", "category", "user")
        read_only_fields = ("path", "numchild", "depth")

    def get_user_name(self, obj):
        return obj.user.get_full_name

    def create(self, validated_data):
        parent = validated_data.pop("parent", None)
        user = self.context['request'].user
        category_pk = self.context['category_pk']

        if parent:
            comment_node = get_object_or_404(Comment, id=parent)
            return comment_node.add_child(user=user, category_id=category_pk, **validated_data)
        else:
            return Comment.add_root(user=user, category_id=category_pk, **validated_data)


class SignUpCourseSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.only("course_name", "is_publish").filter(is_publish=True)
    )
    referral_code = serializers.CharField(required=False)

    class Meta:
        model = SignupCourse
        exclude = ("is_deleted", "deleted_at", "updated_at")

    def create(self, validated_data):
        data = super().create(validated_data)
        referral_code = validated_data.pop("referral_code", None)

        # get phone
        phone = validated_data['phone_number']

        # get referral_code is exits yes or no
        referral_student = Student.objects.filter(referral_code=referral_code).only("student_number")

        Otp.objects.create(mobile_phone=validated_data['phone_number'])
        return data


class AdminCertificateSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.only("student_number", "is_active").filter(is_active=True)
    )
    certificate_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        exclude = ("is_deleted", "deleted_at", "section")

    def get_certificate_image_url(self, obj):
        return obj.image.image_url

    def validate(self, attrs):
        student_section = StudentAccessSection.objects.filter(
            student=attrs["student"],
            is_access=True,
            section__is_last_section=True
        ).select_related("section").only("is_access", "section__is_last_section")

        if not student_section.exists():
            raise exceptions.ValidationError({"message": _("student not appear last section")})
        return attrs


class AdminStudentListCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ("id", "student_name", "get_student_phone")


class SyncAdminCreateStudentSectionSerializer(serializers.Serializer):
    # section = serializers.PrimaryKeyRelatedField(
    #     queryset=Section.objects.only("title", "is_publish").filter(is_publish=True)
    # )
    # course = serializers.PrimaryKeyRelatedField(
    #     queryset=Course.objects.only("course_name", "is_publish").filter(is_publish=True)
    # )
    section = serializers.IntegerField()
    course = serializers.IntegerField()

    def create(self, validated_data):
        section_id = validated_data['section']
        course_id = validated_data['course']

        # دریافت همه دانش‌آموزان موجود برای این دوره
        existing_students = Student.objects.filter(
            student_lesson_course__course_id=course_id,
            student_lesson_course__is_active=True
        ).distinct()

        # دریافت دانش‌آموزانی که از قبل دسترسی دارند
        existing_access = StudentAccessSection.objects.filter(
            section_id=section_id,
            student__in=existing_students
        ).values_list('student_id', flat=True)

        # ایجاد لیست برای bulk_create
        new_access = [
            StudentAccessSection(
                student_id=student_id,
                section_id=section_id
            )
            for student_id in existing_students.values_list('id', flat=True)
            if student_id not in existing_access
        ]

        StudentAccessSection.objects.bulk_create(new_access)

        return {
            'section': section_id,
            "course": course_id,
        }


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEnrollment
        fields = ("id", "student_status", "student")


class DataStudentEnrollmentSerializer(serializers.Serializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.only(
            "student_number",
        ).filter(is_active=True)
    )
    # student_status = serializers.ChoiceField(
    #     choices=StudentStatusEnum.choices
    # )


class CreateStudentEnrollmentSerializer(serializers.Serializer):
    data = DataStudentEnrollmentSerializer(many=True)

    def create(self, validated_data):
        data = validated_data.pop("data")
        class_room_id = self.context['class_room_pk']

        if not data:
            raise exceptions.ValidationError({"message": "you must send student_id and student status"})
        else:
            create_data = [
                StudentEnrollment(
                    student=i['student'],
                    lesson_course_id=class_room_id
                )
                for i in data
            ]
            created = StudentEnrollment.objects.bulk_create(create_data)
            for obj in created:
                post_save.send(
                    sender=StudentEnrollment,
                    instance=obj,
                    created=True
                )
            return {"data": created}
