from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework import permissions

from course.models import Term, Course, UnitSelection
from .paginations import CoursePagination
from .serializers import TermSerializer, CourseSerializer, UnitSelectionSerializer


class TermViewSet(ModelViewSet):
    queryset = Term.objects.all()
    serializer_class = TermSerializer
    pagination_class = CoursePagination

    def get_permissions(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return [permissions.IsAdminUser()]
        return super().get_permissions()


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.select_related("term")
    serializer_class = CourseSerializer

    def get_permissions(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        if "term_pk" in self.kwargs:
            return Course.objects.filter(term_id=self.kwargs["term_pk"]).select_related("term")
        return super().get_queryset()

    def get_serializer_context(self):
        return {'term_pk': self.kwargs["term_pk"]}


class UnitSelectionViewSet(ModelViewSet):
    queryset = UnitSelection.objects.select_related("term", "course", "student", "professor")
    serializer_class = UnitSelectionSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CoursePagination
