import jwt
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password

from rest_framework import generics
from rest_framework import exceptions

from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User, Otp, State, City, Student, Coach, Ticket, TicketRoom, BestStudent
from accounts.validators import MobileRegexValidator


class UserLoginSerializer(serializers.Serializer):
    mobile_phone = serializers.CharField(validators=[MobileRegexValidator])
    password = serializers.CharField(write_only=True, help_text=_("رمز عبور"), style={"input_type": "password"})


class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    image = Base64ImageField(required=False)
    city_name = serializers.SerializerMethodField()
    state_name = serializers.SerializerMethodField()

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise ValidationError({"confirm_password": _("پسورد ها با هم برابر نیست")})
        return attrs

    def validate_password(self, data):
        try:
            validate_password(data)
        except Exception as e:
            raise ValidationError(e)
        return data

    def get_city_name(self, obj):
        return obj.city.city if obj.city else None

    def get_state_name(self, obj):
        return obj.state.state_name if obj.state else None

    class Meta:
        model = User
        exclude = ["last_login", "is_superuser", "groups", "user_permissions", "is_active", "is_verified"]
        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password"}},
            "confirm_password": {"write_only": True},
            "nation_code": {'required': False},
        }

    def create(self, validated_data):
        del validated_data['confirm_password']
        return User.objects.create_user(**validated_data)


class UpdateUserSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False)

    def validate(self, attrs):
        state = attrs.get('state')
        city = attrs.get('city')
        if state and city:
            if not City.objects.filter(city=city, state__state_name=state).exists():
                raise ValidationError({"message": _("لطفا شهر هر استان رو وارد کنید")})
        return attrs

    class Meta:
        model = User
        exclude = ['password', "last_login", "is_superuser", "groups", "user_permissions", "is_active",
                   "is_verified"]
        extra_kwargs = {
            "nation_code": {"required": False}
        }


class OtpLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Otp
        fields = ['mobile_phone']

    def validate(self, attrs):
        phone = attrs['mobile_phone']
        try:
            user = User.objects.get(mobile_phone=attrs['mobile_phone'])
        except User.DoesNotExist:
            raise ValidationError({"message": _("چنین کاربری وجود ندارد لطفا ابتدا ثبت نام کنید")})
        else:
            otp = Otp.objects.filter(mobile_phone=phone).last()
            if user.is_deleted:
                raise ValidationError({"message": _("کاربر گرامی دسترسی شما مسدود شده هست!")})
            if otp:
                if not otp.is_expired:
                    raise ValidationError(
                        {"message": _(f"شما از قبل یه کد دارید لطفا به مدت {otp.time_left_otp} ثانیه صبر کنید ")}
                    )
                if otp.is_expired:
                    otp.delete()
                    raise ValidationError({"message": _("کد otp منقضی شده هست لطفا دوباره درخواست خود را ارسال کنید")})
        return attrs


class VerifyOtpSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate(self, attrs):
        try:
            otp = Otp.objects.get(code=attrs['code'])
        except Otp.DoesNotExist:
            raise ValidationError({"code": _("کد وارد شده اشتباه هست")})
        else:
            if otp.is_expired:
                otp.delete()
                raise ValidationError({"message": _("کد وارد شده منقضی هست لطفا دوباره درخواست خود را ارسال کنید")})
            else:
                user = User.objects.get(mobile_phone=otp.mobile_phone)
                refresh = RefreshToken.for_user(user)
        attrs['refresh'] = str(refresh)
        attrs['access'] = str(refresh.access_token)
        otp.delete()
        return attrs


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ['id', "state_name"]


class CitySerializer(serializers.ModelSerializer):
    state = StateSerializer(read_only=True)

    class Meta:
        model = City
        fields = ['id', "city", "state"]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(min_length=8, style={'input_type': 'password'}, write_only=True)
    new_password = serializers.CharField(min_length=8, style={'input_type': 'password'}, write_only=True)
    confirm_password = serializers.CharField(min_length=8, style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        old_password = attrs.get('old_password')
        confirm_password = attrs.get('confirm_password')
        user = self.context['user']

        if new_password != confirm_password:
            raise ValidationError({"message": _("پسورد ها با هم برابر نیستند")})
        if not user.check_password(old_password):
            raise ValidationError({"message": _("پسورد فعلی شما صحیح نیست")})
        return attrs

    def create(self, validated_data):
        user = self.context['user']
        user.set_password(validated_data['new_password'])
        user.save()
        return user

    def to_representation(self, instance):
        return {"message": _("پسورد با موفقیت عوض شد")}


class ForgetPasswordSerializer(serializers.Serializer):
    mobile_phone = serializers.CharField(validators=[MobileRegexValidator()])

    def validate_mobile_phone(self, data):
        mobile_phone = data
        try:
            user = User.objects.get(mobile_phone=mobile_phone)
        except User.DoesNotExist:
            raise ValidationError({"message": _("چنین کاربری وجود ندارد")})
        if user.is_deleted:
            raise ValidationError({"message": _("حساب شما مسدود میباشد شما اجازه این کار رو ندارید")})
        return data

    def validate_mobile_phone(self, data):
        mobile_phone = data
        try:
            otp = Otp.objects.get(mobile_phone=mobile_phone)
        except Otp.DoesNotExist:
            pass
        else:
            if otp and otp.is_expired:
                otp.delete()
            if otp:
                raise ValidationError({"message": _("شما از قبل یه درخواست دارید لطفا به مدت 2 دقیقه صبر کنید")})
        return data

    def create(self, validated_data):
        otp, created = Otp.objects.get_or_create(mobile_phone=validated_data['mobile_phone'])
        return otp


class ConfirmForgetPasswordSerializer(serializers.Serializer):
    code = serializers.CharField()
    password = serializers.CharField(min_length=8, style={'input_type': 'password'}, write_only=True)
    confirm_password = serializers.CharField(min_length=8, style={'input_type': 'password'}, write_only=True)

    def validate(self, attrs):
        password = attrs.get('password')
        confirm_password = attrs.get('confirm_password')
        if password != confirm_password:
            raise ValidationError({"message": _("پسورد ها باید یکی باشد")})
        try:
            otp = Otp.objects.get(code=attrs['code'])
        except Otp.DoesNotExist:
            raise ValidationError({"message": _("کد اشتباه هست")})
        else:
            if otp.is_expired:
                otp.delete()
                raise ValidationError({"message": _("کد شما منقضی شده هست لطفا دوباره درخواست خود را ارسال کنید")})
        user = User.objects.get(mobile_phone=otp.mobile_phone)
        attrs['user'] = user
        otp.delete()
        return attrs

    def create(self, validated_data):
        user = validated_data['user']
        user.set_password(validated_data['password'])
        user.save()
        return user

    def to_representation(self, instance):
        return {"message": _("پسورد شما با موفقیت تعویض شد و میتوانید به حساب خود لاگین کنید")}


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        exclude = ['deleted_at', "is_deleted", "created_at", "updated_at"]


class CoachSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coach
        exclude = ['deleted_at', "is_deleted", "created_at", "updated_at"]


class TickerRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketRoom
        fields = ['id', "title_room"]

    def create(self, validated_data):
        user = self.context['user']
        return TicketRoom.objects.create(user=user, **validated_data)


class CreateTicketSerializer(serializers.ModelSerializer):
    ticket_image = Base64ImageField()

    class Meta:
        model = Ticket
        fields = ['id', "ticket_body", "ticket_image"]

    def validate(self, attrs):
        ticket_room = generics.get_object_or_404(
            TicketRoom.objects.only("id", "user_id"),
            pk=self.context['room_pk']
        )
        if ticket_room.user_id != self.context['request'].user.id:
            raise exceptions.ValidationError(detail=exceptions.PermissionDenied)
        return attrs

    def create(self, validated_data):
        user_id = self.context['request'].user.id
        room_id = self.context['room_pk']
        return Ticket.objects.create(sender_id=user_id, room_id=room_id, **validated_data)


class ListTicketChatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = ['id']


class UpdateTicketChatSerializer(serializers.ModelSerializer):
    ticket_image = Base64ImageField()
    sender = serializers.CharField(read_only=True, source="sender.mobile_phone")

    class Meta:
        model = Ticket
        fields = ['ticket_body', "ticket_image", "sender", "created_at"]


class ListUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', "mobile_phone", "email", "is_coach"]


class ListBestStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BestStudent
        fields = ["id", "student_image", "description", "attributes", "student"]


class ValidateTokenSerializer(serializers.Serializer):
    token = serializers.CharField()
