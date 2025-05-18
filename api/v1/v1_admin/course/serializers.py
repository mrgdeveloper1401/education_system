from django.shortcuts import get_object_or_404
from rest_framework import serializers, exceptions
from django.utils.translation import gettext_lazy as _

from accounts.models import Student, Otp, Coach
from course.models import Category, Course, Section, SectionFile, SectionVideo, LessonCourse, Certificate, \
    PresentAbsent, SectionQuestion, AnswerQuestion, Comment, SignupCourse, StudentEnrollment, StudentAccessSection


class CreateCategorySerializer(serializers.ModelSerializer):
    parent = serializers.IntegerField(required=False)

    class Meta:
        model = Category
        fields = ('category_name', 'parent', "image", "description")

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
        fields = ("id", 'category_name', "image", "description")


class UpdateCategoryNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('category_name', "image", "description")


class AdminCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        exclude = ('is_deleted', "deleted_at", "category")

    def create(self, validated_data):
        return Course.objects.create(category_id=self.context['category_pk'],**validated_data)


class AdminCreateCourseSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        exclude = ("is_deleted", "deleted_at", "course")
        read_only_fields = ("course",)

    def create(self, validated_data):
        course_id = self.context['course_pk']
        return Section.objects.create(course_id=course_id,**validated_data)


class AdminCourseSectionFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = SectionFile
        fields = ("is_publish", "zip_file", "title", "file_type", "answer")

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
    students = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Student.objects.only("student_number"), required=False
    )

    class Meta:
        model = LessonCourse
        exclude = ('is_deleted', "deleted_at")

    def create(self, validated_data):
        students = validated_data.pop("students", None)
        class_room = LessonCourse.objects.create(**validated_data)

        if students:
            lst = [
                StudentEnrollment(
                    student=i,
                    lesson_course=class_room
                )
                for i in students
            ]
            StudentEnrollment.objects.bulk_create(lst)
        return class_room


class AdminStudentPresentAbsentSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    section_name = serializers.SerializerMethodField()

    class Meta:
        model = PresentAbsent
        fields = ['id', "student_status", "student_name", "section_name", "created_at"]

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
    class Meta:
        model = SignupCourse
        exclude = ("is_deleted", "deleted_at", "updated_at")

    def create(self, validated_data):
        data = super().create(validated_data)
        Otp.objects.create(mobile_phone=validated_data['phone_number'])
        return data


class AdminCertificateSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(
        queryset=Student.objects.only("student_number").filter(is_active=True)
    )
    certificate_image_url = serializers.SerializerMethodField()

    class Meta:
        model = Certificate
        exclude = ("is_deleted", "deleted_at", "section")

    def get_certificate_image_url(self, obj):
        return obj.image.image_url

    def validate(self, attrs):
        student_section = StudentAccessSection.objects.filter(
            student_id=attrs["student_id"],
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
    section = serializers.IntegerField()
    course = serializers.IntegerField()

    def create(self, validated_data):
        section_id = validated_data['section']
        lesson_course = LessonCourse.objects.only("class_name", "is_active").filter(
            is_active=True,
            course_id=validated_data['course']
        )

        if not lesson_course.exists():
            raise exceptions.ValidationError({"message": _("lesson course not exist")})
        else:
            get_lesson_course = lesson_course.last()
            lesson_course_students = get_lesson_course.students.all()
            std_access_section_list = []

            for student in lesson_course_students:
                get_section = StudentAccessSection.objects.filter(
                    section_id=section_id,
                    student=student
                )
                if not get_section.exists():
                    std_access_section_list.append(
                        StudentAccessSection(
                            section_id=section_id,
                            student=student
                        )
                    )
            if std_access_section_list:
                std_created = StudentAccessSection.objects.bulk_create(std_access_section_list)
                return [
                    {
                        "section_id": i.section.id,
                        "student_id": i.student.id,
                    }
                    for i in std_created
                ]
            return []
