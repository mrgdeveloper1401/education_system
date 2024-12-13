from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from course.models import Term, Course
from utils.permissions import CoursePermission
from .serializers import TermSerializer, CourseSerializer


class CategoryViewSet(ModelViewSet):
    queryset = Term.objects.all()
    serializer_class = TermSerializer

    def get_permissions(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return [permissions.IsAdminUser()]
        return super().get_permissions()


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.prefetch_related('term', "student")
    serializer_class = CourseSerializer
    permission_classes = [CoursePermission]

    def get_permissions(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        if "term_pk" in self.kwargs:
            return Course.objects.filter(term_pk=self.kwargs["term_pk"]).prefetch_related("term", "student")
        return super().get_queryset()

    def get_serializer_context(self):
        # if "category_pk" in self.kwargs:
        return {'term_pk': self.kwargs["term_pk"]}
        # return super().get_serializer_context()
