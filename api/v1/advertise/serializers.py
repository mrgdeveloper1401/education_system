from rest_framework.serializers import ModelSerializer
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError

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
    def validate(self, attrs):
        try:
            user = ConsultationRequest.objects.filter(mobile_phone=attrs['mobile_phone']).last()
        except ConsultationRequest.DoesNotExist:
            pass
        else:
            if not user.is_answer:
                raise ValidationError({"message":
                                      _("شما از قبل یه درخواست مشاوره رو دارید لطفا تا تماس همکاران ما لطفا صبر کنیپ")})
        return attrs

    class Meta:
        model = ConsultationRequest
        exclude = ['deleted_at', "is_deleted", "is_answer"]
        # extra_kwargs = {"topic": {"read_only": True}}


class AdminConsultationRequestSerializer(ModelSerializer):

    class Meta:
        model = ConsultationRequest
        exclude = ['deleted_at', "is_deleted"]


class ConsultationRequestAnswerSerializer(ModelSerializer):
    class Meta:
        model = ConsultationRequest
        exclude = ['deleted_at', "is_deleted"]
