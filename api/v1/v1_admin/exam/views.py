from rest_framework import viewsets, permissions

from exam_app.models import Exam, Question, Answer, Score
from . import serializers
from .paginations import ExamPagination


class ExamViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ExamSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = ExamPagination

    def get_queryset(self):
        return Exam.objects.select_related("course").only(
            "id", "course__course_name", "is_active", "start_datetime", "number_of_time", "course_id", "name",
            "description"
        )


class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.QuestionSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Question.objects.filter(exam_id=self.kwargs["exam_pk"]).defer('is_deleted', "deleted_at")


class AnswerViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AnswerSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Answer.objects.filter(question_id=self.kwargs["question_pk"]).defer('is_deleted', "deleted_at")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["question_pk"] = self.kwargs["question_pk"]
        return context


class ScoreViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ScoreSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Score.objects.filter(exam_id=self.kwargs["exam_pk"]).defer('is_deleted', "deleted_at")
