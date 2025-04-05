from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password

from rest_framework import generics
from rest_framework import exceptions

from accounts.models import User, Otp, State, City, Student, Coach, Ticket, TicketRoom, BestStudent, PrivateNotification
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
        fields = ['id', "title_room", "subject_room", "is_close", "created_at"]

    def create(self, validated_data):
        user = self.context['request'].user
        return TicketRoom.objects.create(user=user, **validated_data)


class TicketSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    parent = serializers.IntegerField(required=False)
    reply_name = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ['id', "ticket_body", "ticket_file", "created_at", "sender_name", "parent", "depth", "path",
                  "numchild", "reply", "reply_name", "sender"]
        read_only_fields = ['depth', "path", "numchild", "reply", "sender"]

    def validate(self, attrs):
        request = self.context['request']
        room_pk = self.context['room_pk']

        room = TicketRoom.objects.filter(id=room_pk).only("id")

        if not room:
            raise exceptions.NotFound()

        if hasattr(request.user, "student") or hasattr(request.user, "coach"):
            get_room = TicketRoom.objects.filter(user_id=request.user.id, id=room_pk).only("id")

            if not get_room:
                raise exceptions.NotFound()

        return attrs

    def create(self, validated_data):
        parent = validated_data.pop('parent', None)
        room_id = self.context['room_pk']
        request = self.context['request']

        if request.user.is_staff:
            if parent:
                ticket = generics.get_object_or_404(Ticket, id=parent)
                return ticket.add_child(
                    room_id=room_id, sender_id=ticket.sender_id, reply_id=request.user.id, **validated_data
                )
            else:
                return Ticket.add_root(sender_id=request.user.id, room_id=room_id, **validated_data)

        else:
            if parent:
                ticket = generics.get_object_or_404(Ticket, id=parent)
                return ticket.add_child(
                    room_id=ticket.room_id, sender_id=request.user.id, reply_id=request.user.id, **validated_data
                )
            else:
                return Ticket.add_root(sender_id=request.user.id, room_id=room_id, **validated_data)

    def get_sender_name(self, obj):
        return obj.sender.get_full_name

    def get_reply_name(self, obj):
        return obj.reply.get_full_name if obj.reply else None


class ListBestStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BestStudent
        fields = ["id", "student_image", "description", "attributes", "student"]


class ValidateTokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class UserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateNotification
        fields = ['body', "created_at"]
