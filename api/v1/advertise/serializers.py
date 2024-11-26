from rest_framework.serializers import ModelSerializer

from advertise.models import ConsultationTopic, ConsultationSchedule, ConsultationSlot, ConsultationRequest


class ConsultationTopicSerializer(ModelSerializer):
    class Meta:
        model = ConsultationTopic
        fields = ['id', "name"]


class ConsultationScheduleSerializer(ModelSerializer):
    class Meta:
        model = ConsultationSchedule
        exclude = ['deleted_at', "is_deleted"]


class ConsultationSlotSerializer(ModelSerializer):
    class Meta:
        model = ConsultationSlot
        exclude = ['deleted_at', "is_deleted"]


class UserConsultationRequestSerializer(ModelSerializer):
    class Meta:
        model = ConsultationRequest
        exclude = ['deleted_at', "is_deleted", "is_answer"]


class AdminConsultationRequestSerializer(ModelSerializer):
    class Meta:
        model = ConsultationRequest
        exclude = ['deleted_at', "is_deleted"]


class ConsultationRequestAnswerSerializer(ModelSerializer):
    class Meta:
        model = ConsultationRequest
        exclude = ['deleted_at', "is_deleted"]
