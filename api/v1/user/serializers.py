from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import ValidationError
from django.db.transaction import atomic
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User, Otp
from accounts.validators import MobileRegexValidator


class UserSerializer(serializers.Serializer):
    mobile_phone = serializers.CharField(validators=[MobileRegexValidator()])
    first_name = serializers.CharField()
    last_name = serializers.CharField()

    def validate(self, attrs):
        otp = Otp.objects.filter(mobile_phone=attrs['mobile_phone']).last()
        if otp and otp.is_expired:
            otp.delete()
        else:
            if otp:
                raise ValidationError(
                    {"message": _("شما از قبل درخواست خود را ارسال کرده اید لطفا به مدت دو دقیقه صبر کنید")})
        return attrs

    def create(self, validated_data):
        with atomic():
            user, _ = User.objects.get_or_create(**validated_data)
            Otp.objects.get_or_create(mobile_phone=validated_data['mobile_phone'])
        return user

    def to_representation(self, instance):
        return {'message': _("کد برای شما ارسال خواهد شد")}


class OtpVerifySerializer(serializers.Serializer):
    code = serializers.CharField()
    mobile_phone = serializers.CharField(required=False, validators=[MobileRegexValidator()])

    def validate(self, attrs):
        try:
            otp = Otp.objects.filter(code=attrs['code']).last()
            if otp is None:
                raise ValidationError({"message": _("کد وارد شده اشتباه هست")})
            if otp and otp.is_expired:
                otp.delete()
                raise ValidationError({"message": _("کد وارد شده منقضی شده لطفا دوباره درخواست خود را ارسال نمایید")})
        except Otp.DoesNotExist:
            raise ValidationError({"message": _("کد وارد شده اشتباه هست")})
        else:
            user = User.objects.get(mobile_phone=otp.mobile_phone)
            refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'attrs': attrs
        }


class ResendOtpCodeSerializer(serializers.Serializer):
    mobile_phone = serializers.CharField(validators=[MobileRegexValidator()])

    def validate_mobile_phone(self, value):
        try:
            User.objects.get(mobile_phone=value)
        except User.DoesNotExist:
            raise ValidationError({"message": _("چنین کاربری وجود ندارد لطفا ابتدا ثبت نام کنید")})
        return value

    def create(self, validated_data):
        return Otp.objects.create(mobile_phone=validated_data['mobile_phone'])
