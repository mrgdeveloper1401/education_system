from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from django.utils.translation import gettext_lazy as _

from advertise.models import Advertise, DefineAdvertise


class AdvertiseSerializer(ModelSerializer):
    class Meta:
        model = Advertise
        fields = '__all__'
        extra_kwargs = {
            'answered': {'read_only': True},
        }

    def validate(self, attrs):
        mobile_phone = attrs.get('mobile_phone')
        if Advertise.objects.filter(mobile_phone=mobile_phone, answered=False).exists():
            raise ValidationError({"message": _("شما از قبل یه رزرو داشته اید لطفا تا پاسخ دادن به این رزور صبر کنید")})
        return attrs


class DefineAdvertiseSerializer(ModelSerializer):
    class Meta:
        model = DefineAdvertise
        fields = '__all__'


class AnsweredSlotSerializer(ModelSerializer):
    class Meta:
        model = DefineAdvertise
        fields = '__all__'


class AnsweredAdvertiseSerializer(ModelSerializer):
    slot = AnsweredSlotSerializer(read_only=True)

    class Meta:
        model = Advertise
        fields = '__all__'
