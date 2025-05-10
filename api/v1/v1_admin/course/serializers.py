from django.shortcuts import get_object_or_404
from rest_framework import serializers, exceptions

from accounts.models import Student, Otp, Coach
from course.models import Category, Course, Section, SectionFile, SectionVideo, LessonCourse, Certificate, \
    PresentAbsent, SectionQuestion, AnswerQuestion, Comment, SignupCourse


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


class AdminListCourseSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.only("category_name")
    )

    class Meta:
        model = Course
        exclude = ('is_deleted', "deleted_at")
        read_only_fields = ('course_image',)


class AdminCreateCourseSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.only("category_name")
    )

    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ("category",)

    def create(self, validated_data):
        return Course.objects.create(
            category_id=self.context['category_pk'],
            **validated_data
        )


class AdminUpdateCourseSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.only("category_name")
    )

    class Meta:
        model = Course
        exclude = ('is_deleted', "deleted_at", "updated_at")


class AdminCreateCourseSectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Section
        fields = ('title', "description", "cover_image")

    def create(self, validated_data):
        course_id = self.context['course_pk']
        return Section.objects.create(
            course_id=course_id,
            **validated_data
        )


class AdminListCourseSectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Section
        exclude = ("deleted_at", "is_deleted")


class AdminCreateCourseSectionFileSerializer(serializers.ModelSerializer):

    class Meta:
        model = SectionFile
        fields = ("is_publish", "zip_file", "title", "file_type", "answer")

    def create(self, validated_data):
        return SectionFile.objects.create(section_id=int(self.context['section_pk']), **validated_data)


class AdminListCourseSectionFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionFile
        exclude = ('is_deleted', "deleted_at")


class AdminCreateSectionVideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = SectionVideo
        fields = ['is_publish', "video", "title"]

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
        student = validated_data.pop("students")
        class_room = LessonCourse.objects.create(**validated_data)
        class_room.students.set(student)
        return class_room


class AdminCertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        exclude = ['is_deleted', "deleted_at", "updated_at", "created_at"]


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
        fields = ['id', "question_title", "is_publish", "created_at"]

    def create(self, validated_data):
        section_pk = self.context['section_pk']
        return SectionQuestion.objects.create(section_id=section_pk, **validated_data)


class AnswerQuestionSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=Student.objects.only("student_number"))

    class Meta:
        model = AnswerQuestion
        fields = ['id', "student", "created_at", "rate"]


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
        fields = ['id', "is_publish", "comment_body", "path", "numchild", "depth", "parent", "user_name", "created_at"]
        read_only_fields = ["path", "numchild", "depth"]

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


class ResentOtpCodeSerializer(serializers.Serializer):
    mobile_phone = serializers.CharField()

    def validate(self, attrs):
        if not SignupCourse.objects.filter(phone_number=attrs["mobile_phone"]).exists():
            raise exceptions.ValidationError({"message": "you must sign up in SingUpCourse"})
        return attrs

    def create(self, validated_data):
        phone = validated_data['mobile_phone']
        otp = Otp.objects.filter(mobile_phone=phone).only("mobile_phone", "expired_date").last()

        if otp and otp.is_expired is False:
            raise exceptions.ValidationError({"message": "you can already otp code, please 2 minute wait"})

        return Otp.objects.create(mobile_phone=phone)
