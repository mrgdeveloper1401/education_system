from rest_framework import serializers

from course.models import StudentEnrollment, TeacherEnrollment
from subscription_app.models import AccessCourse


class AdminStudentEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentEnrollment
        exclude = ['is_deleted', "deleted_at"]


class AdminTeacherEnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherEnrollment
        exclude = ['is_deleted', "deleted_at"]
