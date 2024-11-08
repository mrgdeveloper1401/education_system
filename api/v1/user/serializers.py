from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, CharField, SerializerMethodField, Serializer
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User, Otp


class UserSerializer(ModelSerializer):
    school_name = CharField(source='school', read_only=True)
    city_name = CharField(source='city', read_only=True)
    state_name = CharField(source='state', read_only=True)
    image_address = SerializerMethodField()
    confirm_password = CharField(write_only=True, style={'input_type': 'password'})

    def validate(self, attrs):

        # get boolean field
        is_student = attrs.get('is_student')
        is_staff = attrs.get('is_staff')
        is_coach = attrs.get('is_coach')
        state = attrs.get('state')
        city = attrs.get('city')

        # validate password
        if attrs['password'] != attrs['confirm_password']:
            raise ValidationError({"confirm_password": _("پسورد ها با هم برابر نیست")})

        if is_student and (is_staff or is_coach):
            raise ValidationError({"message": _("کاربر فراگیر نمیتواند مربی یا ادمین باشد")})
        if city and state:
            if not state.city.filter(city=city).exists():
                raise ValidationError({"message": _("لطفا شهر مربوط به هر استان رو انتخاب کنید")})
        return attrs

    def validate_password(self, data):
        try:
            validate_password(data)
        except Exception as e:
            raise ValidationError(e)
        return data

    class Meta:
        model = User
        fields = ["id", 'first_name', "last_name", "birth_date", "mobile_phone", "password", "confirm_password",
                  "second_mobile_phone", "grade", "state", "state_name", "city", "city_name", "school", "school_name",
                  "nation_code", "gender", "address", "image", "is_staff", "is_student", "is_coach", "image_base64",
                  "image_address"]
        extra_kwargs = {
            "password": {"write_only": True, "style": {"input_type": "password"}},
            "confirm_password": {"write_only": True},
        }

    def get_image_address(self, obj):
        return obj.image.url if obj.image else None

    def create(self, validated_data):
        del validated_data['confirm_password']
        return User.objects.create_user(**validated_data)


class UpdateUserSerializer(ModelSerializer):
    class Meta:
        model = User
        exclude = ['password', "last_login", "is_superuser", "image_base64", "groups", "user_permissions", "is_active",
                   "is_verified"]

    def validate(self, attrs):

        # get boolean field
        is_student = attrs.get('is_student')
        is_staff = attrs.get('is_staff')
        is_coach = attrs.get('is_coach')
        state = attrs.get('state')
        city = attrs.get('city')

        if is_student and (is_staff or is_coach):
            raise ValidationError({"message": _("کاربر فراگیر نمیتواند مربی یا ادمین باشد")})
        if city and state:
            if not state.city.filter(city=city).exists():
                raise ValidationError({"message": _("لطفا شهر مربوط به هر استان رو انتخاب کنید")})
        return attrs


class OtpLoginSerializer(ModelSerializer):
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
                    raise ValidationError({"message": _("شما از قبل یه کد رو دارید لطفا به مدت 2 دقیقه صبر کنید")})
                if otp.is_expired:
                    otp.delete()
                    raise ValidationError({"message": _("کد otp منقضی شده هست لطفا دوباره درخواست خود را ارسال کنید")})
        return attrs


class VerifyOtpSerializer(Serializer):
    code = CharField()

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
