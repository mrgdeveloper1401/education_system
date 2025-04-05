from rest_framework import serializers

from accounts.models import BestStudent, Student, Coach, User


class AdminBestStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BestStudent
        fields = ["id", 'is_publish', "student", "description", "student_image", "attributes"]


class AdminStudentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        fields = ['id', "student_name", "get_student_phone"]


class AdminCouchListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coach
        fields = ['id', "get_coach_name", "get_coach_phone"]


class AdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', "mobile_phone", "get_full_name"]
