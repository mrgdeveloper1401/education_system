from rest_framework import viewsets, permissions, mixins, exceptions, generics, filters
from django.utils.translation import gettext_lazy as _
from django.db.models import Prefetch

from accounts.models import User
from accounts.permissions import IsCoachUser
from exam_app.models import Exam, Question, Participation, Choice, Answer
from . import serializers
from .pagination import ExamPagination


class ExamViewSet(viewsets.ModelViewSet):
    """
    pagination --> 20 item
    """
    serializer_class = serializers.ExamSerializer
    pagination_class = ExamPagination

    def get_serializer_class(self):
        user = self.request.user

        if self.action == 'create':
            return serializers.CreateExamSerializer

        if self.action == "retrieve" and (user.is_coach or user.is_staff):
            return serializers.CoachAdminExamSerializer

        return super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user

        queryset =  Exam.objects.filter(
            is_active=True,
            ).select_related(
            "course"
        ).prefetch_related(
            Prefetch("questions", queryset=Question.objects.only("id", "exam_id"))
        ).only(
            "name",
            "description",
            "course__course_name",
            "is_active",
            "start_datetime",
            "number_of_time",
            "start_datetime"
        )
        if self.request.user.is_coach is False:
            queryset = queryset.filter(
                user_access__id=self.request.user.id
            )
        if self.action == "retrieve" and (user.is_staff or user.is_coach):
            queryset = queryset.prefetch_related(
                Prefetch(
                    "user_access", queryset=User.objects.filter(is_active=True).only(
                        "first_name",
                        "last_name",
                        "mobile_phone"
                    )
                )
            )
        return queryset

    def get_permissions(self):
        if self.request.method in ['POST', "PUT", "PATCH", "DELETE"]:
            self.permission_classes = (IsCoachUser,)
        else:
            self.permission_classes = (permissions.IsAuthenticated,)
        return super().get_permissions()


class QuestionViewSet(viewsets.ModelViewSet):
    """
    'MC' --> 'چند گزینه‌ای' \n
    'DE', --> 'تشریحی' \n
    filter query --> ?search=MC or ?search=DE
    """
    serializer_class = serializers.QuestionSerializer
    filter_backends = (filters.SearchFilter,)
    search_fields = ("question_type__iexact",)

    def get_serializer_context(self):
        content = super().get_serializer_context()
        content['exam_pk'] = self.kwargs['exam_pk']
        return content

    def get_permissions(self):
        if self.request.method in ['POST', "PUT", "PATCH", "DELETE"]:
            self.permission_classes = (IsCoachUser,)
        else:
            self.permission_classes = (permissions.IsAuthenticated,)
        return super().get_permissions()

    def get_queryset(self):
        return Question.objects.filter(
            is_active=True,
            exam_id=self.kwargs["exam_pk"],
        ).prefetch_related(
            Prefetch(
                "choices", queryset=Choice.objects.only("id", "text", "question_id")
            )
        ).only(
            "name",
            "question_file",
            "max_score",
            "question_type"
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
        if request.user.is_coach is False and request.user.is_staff is False:
            self.check_permission_view_question(request=request)
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        if request.user.is_coach is False and request.user.is_staff is False:
            self.check_permission_view_question(request=request)
        return super().retrieve(request, *args, **kwargs)


class QuestionChoiceViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CreateChoiceSerializer
    permission_classes = (permissions.IsAdminUser,)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['question_pk'] = self.kwargs['question_pk']
        return context

    def get_queryset(self):
        return Choice.objects.filter(question_id=self.kwargs['question_pk']).only(
            "text",
            "is_correct"
        )


class ParticipationViewSet(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           mixins.CreateModelMixin,
                           mixins.UpdateModelMixin,
                           viewsets.GenericViewSet):
    serializer_class = serializers.ParticipationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = Participation.objects.filter(
            exam_id=self.kwargs["exam_pk"],
        ).select_related("exam").only(
            "created_at",
            "exam__name",
            "student_id",
            "is_access",
            "score",
            "created_at",
            "exam__number_of_time"
        )

        #  check request has coach or student
        if self.request.user.is_coach is False:
            queryset = queryset.filter(student__user_id=self.request.user.id)
        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["exam_pk"] = self.kwargs["exam_pk"]
        return context

    def get_serializer_class(self):
        if self.action in ['update', "partial_update"]:
            return serializers.ParticipationCoachSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH']:
            self.permission_classes = (permissions.IsAuthenticated, IsCoachUser)
        return super().get_permissions()


class AnswerViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin
):
    serializer_class = serializers.AnswerSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return Answer.objects.filter(
            participation_id=self.kwargs["participation_pk"],
        ).select_related(
            "participation",
            "question"
        ).only(
            "participation__is_access",
            "question__name",
            "selected_choices",
            "text_answer",
            "given_score",
            "choice_file",
            "created_at"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['participation_pk'] = self.kwargs['participation_pk']
        return context


class CoachScoreAnswerView(generics.UpdateAPIView):
    queryset = Answer.objects.only(
        "given_score",
        "question__name",
        "participation__is_access",
    )
    serializer_class = serializers.AnswerScoreSerializer
    permission_classes = (permissions.IsAuthenticated, IsCoachUser)
