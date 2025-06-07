from rest_framework import viewsets, permissions, mixins, exceptions
from django.utils.translation import gettext_lazy as _

from exam_app.models import Exam, Question, Answer, Score, Participation
from . import serializers
from .pagination import ExamPagination


class ExamViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ExamSerializer
    pagination_class = ExamPagination
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Exam.objects.filter(
            is_active=True,
            user_access__id=self.request.user.id
            ).select_related(
            "course"
        ).only(
            "name",
            "description",
            "course__course_name",
            "is_active",
            "start_datetime",
            "number_of_time",
            "start_datetime"
        )


class QuestionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.QuestionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Question.objects.filter(
            is_active=True,
            exam_id=self.kwargs["exam_pk"],
        ).only(
            "name"
        )

    # check permission user taken the exam
    def check_permission_view_question(self, request):
        get_participation = Participation.objects.filter(
            student__user=request.user,
            exam_id=self.kwargs["exam_pk"],
            is_access=True
        )

        if not get_participation.exists():
            raise exceptions.PermissionDenied(_("you not taken this exam"))

    def list(self, request, *args, **kwargs):
        self.check_permission_view_question(request=request)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        self.check_permission_view_question(request=request)
        return super().retrieve(request, *args, **kwargs)


class ParticipationViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.CreateModelMixin,
                           viewsets.GenericViewSet):
    serializer_class = serializers.ParticipationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Participation.objects.filter(
            exam_id=self.kwargs["exam_pk"],
            student__user_id=self.request.user.id
        ).select_related("exam").only(
            "created_at",
            "exam__name",
            "student_id",
            "is_access"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["exam_pk"] = self.kwargs["exam_pk"]
        return context


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
