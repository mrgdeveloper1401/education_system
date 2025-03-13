from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.db import connection

from accounts.models import TicketReply, BestStudent, Student, Coach, User


class AdminCreateTicketReplySerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = TicketReply
        fields = ["id", 'message', "image", "ticket"]
        read_only_fields = ['ticket']

    def create(self, validated_data):
        return TicketReply.objects.create(
            sender_id=self.context['request'].user.id,
            ticket_id=self.context['ticket_chat_pk'],
            **validated_data
        )


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
