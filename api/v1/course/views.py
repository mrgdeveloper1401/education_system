from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from course.models import Term, Course, UnitSelection
from .paginations import CoursePagination
from .serializers import TermSerializer, CourseSerializer, UnitSelectionSerializer


class TermViewSet(ModelViewSet):
    queryset = Term.objects.select_related('department')
    serializer_class = TermSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CoursePagination


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.filter(is_publish=True).select_related('department', "term")
    serializer_class = CourseSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CoursePagination


class UnitSelectionViewSet(ModelViewSet):
    queryset = UnitSelection.objects.select_related("term", "course", "student", "professor")
    serializer_class = UnitSelectionSerializer
    permission_classes = [IsAdminUser]
    pagination_class = CoursePagination
