from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from django.utils import timezone

from advertise.tasks import send_sms_accept_advertise

from advertise.models import ConsultationTopic, ConsultationSchedule, ConsultationSlot, ConsultationRequest


class ConsultationTopicSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationTopic
        fields = ('id', "name")


class ConsultationScheduleSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConsultationSchedule
        exclude = ('deleted_at', "is_deleted")


class ConsultationSlotSerializer(serializers.ModelSerializer):
    schedule = serializers.PrimaryKeyRelatedField(
        queryset=ConsultationSlot.objects.only("date", "is_available").filter(is_available=True)
    )
    class Meta:
        model = ConsultationSlot
        exclude = ('deleted_at', "is_deleted")


class UserConsultationRequestSerializer(serializers.ModelSerializer):
    slot = serializers.PrimaryKeyRelatedField(
        queryset=ConsultationSlot.objects.only(
            "date",
            "is_available"
        ).filter(
            is_available=True,
            date__gte=timezone.now().date()
        )
    )
    def validate(self, attrs):
        try:
            req = ConsultationRequest.objects.filter(mobile_phone=attrs['mobile_phone']).only("mobile_phone").last()
        except ConsultationRequest.DoesNotExist:
            pass
        else:
            if req and req.is_answer is False:
                raise ValidationError({"message":
                                      _("شما از قبل یه درخواست مشاوره رو دارید لطفا تا تماس همکاران ما لطفا صبر کنیپ")})
        return attrs

    class Meta:
        model = ConsultationRequest
        exclude = ('deleted_at', "is_deleted")

    def create(self, validated_data):
        data = super().create(validated_data)
        send_sms_accept_advertise.delay(data.mobile_phone, str(data.slot.date))
        return data

    def to_representation(self, instance):
        request = self.context['request']
        data = super().to_representation(instance)

        if not request.user.is_staff:
            data.pop("is_answer", None)

        return data

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get('request')
        if not request.user.is_staff:
            fields.pop('is_answer', None)
        return fields


class AdminConsultationRequestSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConsultationRequest
        exclude = ('deleted_at', "is_deleted")


class ConsultationRequestAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsultationRequest
        exclude = ('deleted_at', "is_deleted")
