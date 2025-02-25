from rest_framework import viewsets, permissions

from course.models import StudentEnrollment, TeacherEnrollment
from subscription_app import models
from . import serializers
from .pagination import TeacherStudentEnrollmentPagination


class AdminStudentEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = StudentEnrollment.objects.only(
        "id", "created_at", "updated_at", "student_id", "course_id", "status"
    )
    serializer_class = serializers.AdminStudentEnrollmentSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = TeacherStudentEnrollmentPagination


class AdminTeacherEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = TeacherEnrollment.objects.only(
        "id", "created_at", "updated_at", "role", "coach_id", "course_id"
    )
    serializer_class = serializers.AdminTeacherEnrollmentSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = TeacherStudentEnrollmentPagination
