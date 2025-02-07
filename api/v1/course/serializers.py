from rest_framework import serializers
from course.models import Course, Category, Comment, Section, SectionImage
from rest_framework.generics import get_object_or_404
from drf_spectacular.utils import extend_schema_field
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from images.models import Image


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


class UpdateCategoryNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['category_name']


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


class SectionImageSerializer(serializers.ModelSerializer):
    image_address = serializers.SerializerMethodField()

    class Meta:
        model = SectionImage
        fields = ["image_address"]

    def get_image_address(self, obj):
        return obj.image.image_url


class ListSectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        fields = ['id', "title"]


class SectionSerializer(serializers.ModelSerializer):
    section_image = SectionImageSerializer(many=True, required=False)

    class Meta:
        model = Section
        exclude = ['is_deleted', "deleted_at", "is_available", "course", "id"]
        extra_kwargs = {
            "course": {'read_only': True},
        }


class CreateSectionImageSerializer(serializers.Serializer):
    class Meta:
        model = SectionImage
        fields = ['image']


class CreateSectionSerializer(serializers.ModelSerializer):
    section_image = CreateSectionImageSerializer(many=True, required=False)

    class Meta:
        model = Section
        fields = ['section_image', "video", "pdf_file", "title", "description", "is_available"]
        extra_kwargs = {
            "is_available": {'default': True},
        }

    def validate(self, attrs):
        video = attrs.get('video')
        pdf_file = attrs.get('pdf_file')
        if not video and not pdf_file:
            raise ValidationError({"message": _("video or pdf file must be set")})
        return attrs

    def create(self, validated_data):
        course_pk = self.context['course_pk']
        section_image = self.initial_data.getlist('section_image')
        section = Section.objects.create(course_id=course_pk, **validated_data)

        image_data_list = []
        images = []

        for image_data in section_image:
            images.append(
                Image(
                    image=image_data,
                )
            )
        Image.objects.bulk_create(images)

        for i in images:
            image_data_list.append(
                SectionImage(
                    section=section, image=i
                )
            )
        SectionImage.objects.bulk_create(image_data_list)
        return section


# class LessonByTakenStudentSerializer(serializers.ModelSerializer):
#     course = serializers.CharField()
#     student = serializers.CharField()
#
#     class Meta:
#         model = LessonTakenByStudent
#         exclude = ['deleted_at', "is_deleted"]
#
#
# class LessonTakenByCoachSerializer(serializers.ModelSerializer):
#     course = serializers.CharField()
#     coach = serializers.CharField()
#
#     class Meta:
#         model = LessonTakenByCoach
#         exclude = ["is_deleted", "deleted_at"]
#
#
# class ScoreSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Score
#         fields = '__all__'
#         extra_kwargs = {
#             "coach": {'read_only': True}
#         }
#
#     def create(self, validated_data):
#         user = self.context['user']
#         coach = Coach.objects.get(user=user)
#         return Coach.objects.create(coach=coach, **validated_data)


class CommentSerializer(serializers.ModelSerializer):
    course = serializers.CharField(read_only=True)
    student = serializers.CharField(read_only=True)

    class Meta:
        model = Comment
        exclude = ['is_deleted', "deleted_at", "user"]
        extra_kwargs = {
            "course": {'read_only': True},
            "is_publish": {'read_only': True},
        }

    def create(self, validated_data):
        user = self.context['user']
        course_pk = self.context['course_pk']
        return Comment.objects.create(course_id=course_pk, user=user, **validated_data)


# class PracticeSerializer(serializers.ModelSerializer):
#     coach = serializers.CharField(read_only=True)
#     course = serializers.CharField(read_only=True)
#
#     class Meta:
#         model = Practice
#         exclude = ['is_deleted', "deleted_at", "updated_at"]
#
#     def create(self, validated_data):
#         user = self.context['user']
#         coach = Coach.objects.get(user=user)
#         course_pk = self.context['course_pk']
#         return Practice.objects.create(coach=coach, course_id=course_pk, **validated_data)


# class PracticeSubmitSerializer(serializers.ModelSerializer):
#     student = serializers.CharField(read_only=True)
#     practice = serializers.CharField(read_only=True)
#
#     class Meta:
#         model = PracticeSubmission
#         exclude = ['is_deleted', "deleted_at"]
#         extra_kwargs = {
#             'student': {'read_only': True},
#             "practice": {'read_only': True},
#             "grade": {"read_only": True},
#         }
#
#     def create(self, validated_data):
#         user = self.context['user']
#         student = Student.objects.get(user=user)
#         practice_pk = self.context['practice_pk']
#         return PracticeSubmission.objects.create(student=student, practice_id=practice_pk, **validated_data)
#
#     def validate(self, attrs):
#         try:
#             practice = Practice.objects.get(pk=self.context['practice_pk'])
#         except Practice.DoesNotExist:
#             raise ValidationError({"message": _("چنین تمرینی وجود نداره")})
#         else:
#             if practice.expired_practice < timezone.now():
#                 raise ValidationError({"message": _("ارسال وجود تمرین در این بازه وجود نداره")})
#         return attrs
#
#
# class QuizSerializer(serializers.ModelSerializer):
#     coach = serializers.CharField(read_only=True)
#     course = serializers.CharField(read_only=True)
#
#     class Meta:
#         model = Quiz
#         exclude = ['is_deleted', "deleted_at"]
#
#     def create(self, validated_data):
#         user = self.context['user']
#         course_pk = self.context['course_pk']
#         coach = Coach.objects.get(user=user)
#         return Quiz.objects.create(course_id=course_pk, coach=coach, **validated_data)
#
#
# class QuestionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Question
#         exclude = ['is_deleted', "deleted_at"]
#         extra_kwargs = {
#             "quiz": {"read_only": True}
#         }
#
#     def create(self, validated_data):
#         quiz_pk = self.context['quiz_pk']
#         return Question.objects.create(quiz_id=quiz_pk, **validated_data)
#
#
# class ClassRoomSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ClassRoom
#         exclude = ['is_deleted', "deleted_at"]
#         extra_kwargs = {
#             "course": {"read_only": True},
#         }
#
#     def create(self, validated_data):
#         course_pk = self.context['course_pk']
#         class_room = ClassRoom.objects.create(course_id=course_pk)
#         class_room.student.set(validated_data['student'])
#         class_room.coach.st(validated_data['coach'])
#         class_room.save()
