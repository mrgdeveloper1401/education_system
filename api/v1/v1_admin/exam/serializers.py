from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from exam_app.models import Exam, Question, Answer, Score


class ExamSerializer(serializers.ModelSerializer):
    exam_course_name = serializers.SerializerMethodField()
    is_done_exam = serializers.SerializerMethodField()
    exam_end_date = serializers.SerializerMethodField()

    class Meta:
        model = Exam
        exclude = ['is_deleted', "deleted_at", "created_at", "updated_at"]

    def get_exam_course_name(self, obj):
        return obj.course.course_name

    def get_is_done_exam(self, obj):
        return obj.is_done_exam

    def get_exam_end_date(self, obj):
        return obj.exam_end_date


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        exclude = ['is_deleted', "deleted_at"]


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        exclude = ['is_deleted', "deleted_at", "student_ip_address"]
        extra_kwargs = {
            "is_active": {"default": True},
        }

    def create(self, validated_data):
        return Answer.objects.create(student_ip_address=self.context['request'].META['REMOTE_ADDR'], **validated_data)


class ScoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Score
        exclude = ['is_deleted', "deleted_at"]
