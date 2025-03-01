from rest_framework import viewsets, permissions

from exam_app.models import Exam, Question, Answer, Score
from . import serializers
from .pagination import ExamPagination


class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ExamSerializer
    queryset = Exam.objects.select_related("course").only(
        "id", "course__course_name", "name", "description", "created_at", "start_datetime", "number_of_time"
    )
    pagination_class = ExamPagination


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.QuestionSerializer

    def get_queryset(self):
        return Question.objects.only("id", "exam", "name").filter(exam_id=self.kwargs["exam_pk"])


class AnswerViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AnswerSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Answer.objects.filter(question_id=self.kwargs["question_pk"], student=self.request.user.student).only(
            "id", "question", "answer", "created_at"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['question_pk'] = self.kwargs["question_pk"]
        return context


class ScoreViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ScoreSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Score.objects.filter(exam_id=self.kwargs['exam_pk'], student=self.request.user.student).only(
            "id", "score", "exam", "created_at"
        )
