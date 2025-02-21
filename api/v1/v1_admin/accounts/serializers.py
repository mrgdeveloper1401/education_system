from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions

from accounts.models import TicketReply, BestStudent, Student, BestStudentAttribute


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


class AdminCreateBestStudentSerializer(serializers.ModelSerializer):
    student = serializers.CharField(help_text=_("enter user mobile phone number"),
                                    source="student.user.mobile_phone")

    class Meta:
        model = BestStudent
        fields = ['is_publish', "student", "description"]

    def validate(self, attrs):
        try:
            user_phone = attrs["student"]['user']['mobile_phone']
            student = Student.objects.get(user__mobile_phone=user_phone)
        except Student.DoesNotExist:
            raise exceptions.ValidationError({"message": _(f"student {user_phone} dose not exits")})
        attrs['student'] = student
        return attrs

    def create(self, validated_data):
        return BestStudent.objects.create(is_publish=True, student=validated_data['student'])


class AdminListBestStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BestStudent
        fields = ['id', "created_at", "is_publish", "student", "get_full_name"]


class AdminCreateBestStudentAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BestStudentAttribute
        fields = ['attribute']

    def create(self, validated_data):
        return BestStudentAttribute.objects.create(
            best_student_id=self.context['best_student_pk'],
            **validated_data
        )


class AdminListBestStudentAttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BestStudentAttribute
        fields = ['id', "attribute", "best_student", "created_at"]
