# TODO, remove adrf project
from django.core.cache import cache
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from drf_spectacular.utils import extend_schema_field

from rest_framework import generics
from rest_framework import exceptions
from rest_framework_simplejwt.tokens import RefreshToken

from apps.account_app.models import (
    User,
    State,
    City,
    Student,
    Coach,
    Ticket,
    TicketRoom,
    BestStudent,
    PrivateNotification,
    Invitation,
)
from apps.account_app.validators import MobileRegexValidator
from base.utils.config import get_client_ip


class UserLoginSerializer(serializers.Serializer):
    mobile_phone = serializers.CharField(validators=(MobileRegexValidator(),))
    password = serializers.CharField(
        write_only=True, help_text=_("رمز عبور"), style={"input_type": "password"}
    )

    def validate(self, attrs):
        mobile_phone = attrs.get("mobile_phone")
        password = attrs.get("password")

        # filter user
        user = User.objects.filter(mobile_phone=mobile_phone).only(
            "mobile_phone",
            "first_name",
            "last_name",
            "is_coach",
            "is_staff",
            "is_active",
            "password",
        )
        if user:
            # get user
            get_user = user.first()
            check_user_password = get_user.check_password(password)
            if not check_user_password:
                raise serializers.ValidationError(
                    {"detail": "mobile phone or password is invalid"}
                )
            else:
                attrs["user"] = get_user

        return attrs


class UserSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )
    # image = Base64ImageField(required=False)
    city_name = serializers.SerializerMethodField()
    state_name = serializers.SerializerMethodField()
    # student_referral_code = serializers.SerializerMethodField(allow_null=True)
    referral_code = serializers.CharField(required=False)

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise ValidationError({"confirm_password": _("پسورد ها با هم برابر نیست")})
        return attrs

    def validate_password(self, data):
        try:
            validate_password(data)
        except Exception as e:
            raise ValidationError(e)
        return data

    @extend_schema_field(serializers.CharField())
    def get_city_name(self, obj):
        return obj.city.city if obj.city else None

    @extend_schema_field(serializers.CharField())
    def get_state_name(self, obj):
        return obj.state.state_name if obj.state else None

    # @extend_schema_field(serializers.CharField())
    # def get_student_referral_code(self, obj):
    #     user = self.context['request'].user
    #     if hasattr(user, "student") and user.student:
    #         return obj.student.referral_code
    #     else:
    #         return None

    class Meta:
        model = User
        exclude = (
            "last_login",
            "is_superuser",
            "groups",
            "user_permissions",
            "is_active",
            "is_verified",
        )
        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password"}},
            "confirm_password": {"write_only": True},
            "nation_code": {"required": False},
        }

    def create(self, validated_data):
        # Remove confirm_password as it's no longer needed
        validated_data.pop("confirm_password", None)

        # Extract referral_code if exists
        referral_code = validated_data.pop("referral_code", None)
        referral_student = None

        # Validate referral code if provided
        if referral_code:
            try:
                referral_student = Student.objects.get(referral_code=referral_code)
            except Student.DoesNotExist:
                raise exceptions.ValidationError(
                    {"referral_code": _("Referral code is invalid")}
                )

        # Create user
        user = User.objects.create_user(**validated_data)

        # Create invitation if referral exists
        if referral_student and hasattr(user, "student"):
            Invitation.objects.create(
                from_student=referral_student, to_student=user.student
            )

        return user


class UpdateUserSerializer(serializers.ModelSerializer):
    image = Base64ImageField(required=False)

    def validate(self, attrs):
        state = attrs.get("state")
        city = attrs.get("city")
        if state and city:
            if not City.objects.filter(city=city, state__state_name=state).exists():
                raise ValidationError({"message": _("لطفا شهر هر استان رو وارد کنید")})
        return attrs

    class Meta:
        model = User
        exclude = (
            "password",
            "last_login",
            "is_superuser",
            "groups",
            "user_permissions",
            "is_active",
            "is_verified",
        )
        extra_kwargs = {"nation_code": {"required": False}}


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ("id", "state_name")


class CitySerializer(serializers.ModelSerializer):
    state = StateSerializer(read_only=True)

    class Meta:
        model = City
        fields = ("id", "city", "state")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def to_representation(self, instance):
        return {"message": _("پسورد با موفقیت عوض شد")}


class ForgetPasswordSerializer(serializers.Serializer):
    mobile_phone = serializers.CharField(validators=(MobileRegexValidator(),))


class ConfirmForgetPasswordSerializer(serializers.Serializer):
    code = serializers.CharField()
    password = serializers.CharField()
    confirm_password = serializers.CharField()
    mobile_phone = serializers.CharField(
        validators=[
            MobileRegexValidator(),
        ]
    )

    def validate(self, attrs):
        password = attrs.get("password")
        confirm_password = attrs.get("confirm_password")

        if password != confirm_password:
            raise ValidationError(
                {"detail": "password must be same"}, code="password_not_same"
            )

        return attrs


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Student
        exclude = ("deleted_at", "is_deleted", "created_at", "updated_at")


class CoachSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coach
        exclude = ("deleted_at", "is_deleted", "created_at", "updated_at")


class TickerRoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketRoom
        fields = ("id", "title_room", "subject_room", "is_close", "created_at")

    def create(self, validated_data):
        user = self.context["request"].user
        return TicketRoom.objects.create(user=user, **validated_data)


class TicketSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()
    parent = serializers.IntegerField(required=False)
    reply_name = serializers.SerializerMethodField()
    user_admin = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = (
            "id",
            "ticket_body",
            "ticket_file",
            "created_at",
            "sender_name",
            "parent",
            "depth",
            "path",
            "numchild",
            "reply",
            "reply_name",
            "sender",
            "user_admin",
        )
        read_only_fields = ("depth", "path", "numchild", "reply", "sender")

    def validate(self, attrs):
        request = self.context["request"]
        room_pk = self.context["room_pk"]

        room = TicketRoom.objects.filter(id=room_pk).only("id")

        if not room:
            raise exceptions.NotFound()

        if hasattr(request.user, "student") or (
            hasattr(request.user, "coach") and not request.user.is_staff
        ):
            get_room = TicketRoom.objects.filter(
                user_id=request.user.id, id=room_pk
            ).only("id")

            if not get_room:
                raise exceptions.NotFound()

        attrs["validate_room"] = room
        return attrs

    def create(self, validated_data):
        parent = validated_data.pop("parent", None)
        room_id = self.context["room_pk"]
        request = self.context["request"]

        room = validated_data.pop("validate_room")

        if room.first().is_close:
            raise exceptions.ValidationError({"message": "this room has been closed"})

        if request.user.is_staff:
            if parent:
                ticket = generics.get_object_or_404(Ticket, id=parent)
                return ticket.add_child(
                    room_id=room_id,
                    sender_id=ticket.sender_id,
                    reply_id=request.user.id,
                    **validated_data,
                )
            else:
                return Ticket.add_root(
                    sender_id=request.user.id, room_id=room_id, **validated_data
                )

        else:
            if parent:
                ticket = generics.get_object_or_404(Ticket, id=parent)
                return ticket.add_child(
                    room_id=ticket.room_id,
                    sender_id=request.user.id,
                    reply_id=request.user.id,
                    **validated_data,
                )
            else:
                return Ticket.add_root(
                    sender_id=request.user.id, room_id=room_id, **validated_data
                )

    @extend_schema_field(serializers.CharField())
    def get_sender_name(self, obj):
        return obj.sender.get_full_name

    @extend_schema_field(serializers.CharField())
    def get_reply_name(self, obj):
        return obj.reply.get_full_name if obj.reply else None

    @extend_schema_field(serializers.BooleanField())
    def get_user_admin(self, obj):
        return obj.sender.is_staff


class ListBestStudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = BestStudent
        fields = ("id", "student_image", "description", "attributes", "student")


class ValidateTokenSerializer(serializers.Serializer):
    token = serializers.CharField()


class UserNotificationSerializer(serializers.ModelSerializer):
    user_fullname = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField())
    def get_user_fullname(self, obj):
        return obj.user.get_full_name

    class Meta:
        model = PrivateNotification
        fields = (
            "id",
            "user_fullname",
            "title",
            "body",
            "created_at",
            "is_read",
            "char_link",
            "notification_type",
        )


class CreateUserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateNotification
        fields = ("title", "body", "user", "notification_type", "char_link")


class PatchUserNotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateNotification
        fields = ("is_read",)


class RequestPhoneSerializer(serializers.Serializer):
    mobile_phone = serializers.CharField(validators=(MobileRegexValidator(),))


class RequestPhoneVerifySerializer(serializers.Serializer):
    mobile_phone = serializers.CharField(validators=(MobileRegexValidator(),))
    code = serializers.CharField()

    def validate(self, attrs):
        request = self.context["request"]

        user_ip = get_client_ip(request)

        phone = attrs.get("mobile_phone")
        code = attrs.get("code")

        cache_key = f"otp_{phone}_{code}_{user_ip}"
        get_cache_key = cache.get(cache_key)
        if not get_cache_key:
            raise ValidationError(
                {"detail": "code is invalid or expired"}, code="wrong_code"
            )

        else:
            # get user
            user = (
                User.objects.filter(mobile_phone=attrs["mobile_phone"])
                .only(
                    "mobile_phone",
                    "is_staff",
                    "is_coach",
                    "first_name",
                    "last_name",
                    "is_active",
                )
                .last()
            )

            # check active user
            if user.is_active is False:
                raise exceptions.ValidationError(
                    {"message": "user is banned"}, code="user_ban"
                )
            else:
                # generate token
                token = RefreshToken.for_user(user)

                # otp delete
                cache.delete(cache_key)

                attrs["data"] = {
                    "access": str(token.access_token),
                    "refresh": str(token),
                }
                attrs["is_coach"] = str(user.is_coach)
                attrs["is_staff"] = str(user.is_staff)
                attrs["full_name"] = user.get_full_name

        return attrs


class InvitationSerializer(serializers.ModelSerializer):
    to_student_full_name = serializers.SerializerMethodField()

    @extend_schema_field(serializers.CharField())
    def get_to_student_full_name(self, obj):
        return obj.to_student.user.get_full_name

    class Meta:
        model = Invitation
        fields = ("id", "to_student_full_name", "created_at")
