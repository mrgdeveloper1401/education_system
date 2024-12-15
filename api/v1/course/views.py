from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet
from rest_framework import permissions
from rest_framework.generics import get_object_or_404

from accounts.models import Student, Coach
from course.models import Term, Course, Section, LessonTakenByStudent, LessonTakenByCoach, Score, Comment, Practice, \
    PracticeSubmission, Quiz
from utils.pagination import LessonTakenPagination
from utils.permissions import CoursePermission, StudentPermission, CoachPermission, EditScorePermission, \
    CommentPermission, PracticePermission, SubmitPracticePermissions, QuizPermission
from .serializers import TermSerializer, CourseSerializer, SectionSerializer, LessonByTakenStudentSerializer, \
    LessonTakenByCoachSerializer, ScoreSerializer, CommentSerializer, PracticeSerializer, PracticeSubmitSerializer, \
    QuizSerializer


class CategoryViewSet(ModelViewSet):
    queryset = Term.objects.all()
    serializer_class = TermSerializer

    def get_permissions(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return [permissions.IsAdminUser()]
        return super().get_permissions()


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.select_related('term')
    serializer_class = CourseSerializer
    permission_classes = [CoursePermission]

    def get_permissions(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        if "term_pk" in self.kwargs:
            return Course.objects.filter(term_id=self.kwargs["term_pk"]).select_related("term")
        return super().get_queryset()

    def get_serializer_context(self):
        if "term_pk" in self.kwargs:
            return {'term_pk': self.kwargs["term_pk"]}
        return super().get_serializer_context()


class SectionViewSet(ModelViewSet):
    queryset = Section.objects.select_related('course')
    serializer_class = SectionSerializer

    def get_permissions(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        term = get_object_or_404(Term, id=self.kwargs["term_pk"])
        course = get_object_or_404(Course, term_id=term, id=self.kwargs["course_pk"])
        section = Section.objects.filter(course_id=course)
        return section

    def get_serializer_context(self):
        return {"course_pk": self.kwargs["course_pk"]}


class LessonByStudentTakenViewSet(ReadOnlyModelViewSet):
    # queryset = LessonTakenByStudent.objects.select_related("course", "student")
    serializer_class = LessonByTakenStudentSerializer
    permission_classes = [StudentPermission]
    pagination_class = LessonTakenPagination

    def get_queryset(self):
        student = get_object_or_404(Student, user=self.request.user)
        return LessonTakenByStudent.objects.filter(student=student).select_related("student__user", "course")


class LessonByCoachTakenViewSet(ReadOnlyModelViewSet):
    serializer_class = LessonTakenByCoachSerializer
    permission_classes = [CoachPermission]
    pagination_class = LessonTakenPagination

    def get_queryset(self):
        coach = get_object_or_404(Coach, user=self.request.user)
        return LessonTakenByCoach.objects.filter(coach=coach).select_related("coach__user", "course")


class ScoreViewSet(ModelViewSet):
    serializer_class = ScoreSerializer
    queryset = Score.objects.all()
    permission_classes = [EditScorePermission]

    def get_serializer_context(self):
        return {"user": self.request.user}


class CommentViewSet(ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [CommentPermission]

    def get_queryset(self):
        term = get_object_or_404(Term, pk=self.kwargs['term_pk'])
        course = get_object_or_404(Course, term=term, pk=self.kwargs['course_pk'])
        return Comment.objects.filter(course=course).select_related('student__user', "course")

    def get_serializer_context(self):
        return {
            "user": self.request.user,
            "course_pk": self.kwargs["course_pk"]
        }


class PracticeViewSet(ModelViewSet):
    serializer_class = PracticeSerializer
    permission_classes = [PracticePermission]

    def get_queryset(self):
        course = get_object_or_404(Course, pk=self.kwargs["course_pk"])
        return Practice.objects.filter(course=course).select_related('coach__user', "course")

    def get_serializer_context(self):
        return {
            "user": self.request.user,
            "course_pk": self.kwargs['course_pk']
        }


class SubmitPracticeViewSet(ModelViewSet):
    serializer_class = PracticeSubmitSerializer
    permission_classes = [SubmitPracticePermissions]

    def get_queryset(self):
        course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
        practice = get_object_or_404(Practice, course=course, pk=self.kwargs['practice_pk'])
        return PracticeSubmission.objects.filter(practice=practice, student__user=self.request.user).select_related(
            "student__user", "practice"
        )

    def get_serializer_context(self):
        return {
            "user": self.request.user,
            "practice_pk": self.kwargs['practice_pk'],
            "course_pk": self.kwargs['course_pk']
        }


class QuizViewSet(ModelViewSet):
    serializer_class = QuizSerializer
    # permission_classes = [QuizPermission]

    def get_queryset(self):
        term = get_object_or_404(Term, pk=self.kwargs['term_pk'])
        course = get_object_or_404(Course, term=term, pk=self.kwargs['course_pk'])
        return Quiz.objects.filter(course=course).select_related('course', "coach__user")

    def get_serializer_context(self):
        return {
            "user": self.request.user,
            "course_pk": self.kwargs['course_pk'],
        }