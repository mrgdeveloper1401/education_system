from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from rest_framework.validators import ValidationError

from accounts.models import Coach, Student
from course.models import Course, Term, Section, LessonTakenByStudent, LessonTakenByCoach, Score, Comment, Practice, \
    PracticeSubmission, Quiz


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = ['id', "term_name"]


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        exclude = ['deleted_at', "is_deleted"]


class SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Section
        exclude = ['is_deleted', "deleted_at"]
        extra_kwargs = {
            "course": {'read_only': True},
        }

    def create(self, validated_data):
        course_pk = self.context['course_pk']
        return Section.objects.create(course_id=course_pk, **validated_data)


class LessonByTakenStudentSerializer(serializers.ModelSerializer):
    course = serializers.CharField()
    student = serializers.CharField()

    class Meta:
        model = LessonTakenByStudent
        exclude = ['deleted_at', "is_deleted"]


class LessonTakenByCoachSerializer(serializers.ModelSerializer):
    course = serializers.CharField()
    coach = serializers.CharField()

    class Meta:
        model = LessonTakenByCoach
        exclude = ["is_deleted", "deleted_at"]


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        fields = '__all__'
        extra_kwargs = {
            "coach": {'read_only': True}
        }

    def create(self, validated_data):
        user = self.context['user']
        coach = Coach.objects.get(user=user)
        return Coach.objects.create(coach=coach, **validated_data)


class CommentSerializer(serializers.ModelSerializer):
    course = serializers.CharField(read_only=True)
    student = serializers.CharField(read_only=True)

    class Meta:
        model = Comment
        exclude = ['is_deleted', "deleted_at"]
        extra_kwargs = {
            "course": {'read_only': True},
            "student": {'read_only': True},
            "is_publish": {'read_only': True},
        }

    def create(self, validated_data):
        user = self.context['user']
        student = Student.objects.get(user=user)
        course_pk = self.context['course_pk']
        return Comment.objects.create(course_id=course_pk, student=student, **validated_data)


class PracticeSerializer(serializers.ModelSerializer):
    coach = serializers.CharField(read_only=True)
    course = serializers.CharField(read_only=True)

    class Meta:
        model = Practice
        exclude = ['is_deleted', "deleted_at", "updated_at"]

    def create(self, validated_data):
        user = self.context['user']
        coach = Coach.objects.get(user=user)
        course_pk = self.context['course_pk']
        return Practice.objects.create(coach=coach, course_id=course_pk, **validated_data)


class PracticeSubmitSerializer(serializers.ModelSerializer):
    student = serializers.CharField(read_only=True)
    practice = serializers.CharField(read_only=True)

    class Meta:
        model = PracticeSubmission
        exclude = ['is_deleted', "deleted_at"]
        extra_kwargs = {
            'student': {'read_only': True},
            "practice": {'read_only': True},
            "grade": {"read_only": True},
        }

    def create(self, validated_data):
        user = self.context['user']
        student = Student.objects.get(user=user)
        practice_pk = self.context['practice_pk']
        return PracticeSubmission.objects.create(student=student, practice_id=practice_pk, **validated_data)

    def validate(self, attrs):
        try:
            practice = Practice.objects.get(pk=self.context['practice_pk'])
        except Practice.DoesNotExist:
            raise ValidationError({"message": _("چنین تمرینی وجود نداره")})
        else:
            if practice.expired_practice < timezone.now():
                raise ValidationError({"message": _("ارسال وجود تمرین در این بازه وجود نداره")})
        return attrs


class QuizSerializer(serializers.ModelSerializer):
    coach = serializers.CharField(read_only=True)
    course = serializers.CharField(read_only=True)

    class Meta:
        model = Quiz
        exclude = ['is_deleted', "deleted_at"]

    def create(self, validated_data):
        user = self.context['user']
        course_pk = self.context['course_pk']
        coach = Coach.objects.get(user=user)
        return Quiz.objects.create(course_id=course_pk, coach=coach, **validated_data)
