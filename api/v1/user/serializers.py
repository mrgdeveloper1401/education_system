from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer, CharField, SerializerMethodField
from django.utils.translation import gettext_lazy as _

from accounts.models import User


class UserSerializer(ModelSerializer):
    school_name = CharField(source='school', read_only=True)
    city_name = CharField(source='city', read_only=True)
    state_name = CharField(source='state', read_only=True)
    image_address = SerializerMethodField()

    def validate(self, attrs):
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

    class Meta:
        model = User
        fields = ["id",
                  'first_name',
                  "last_name",
                  "birth_date",
                  "mobile_phone",
                  "second_mobile_phone",
                  "grade",
                  "state",
                  "state_name",
                  "city",
                  "city_name",
                  "school",
                  "school_name",
                  "nation_code",
                  "gender",
                  "address",
                  "image",
                  "is_staff",
                  "is_student",
                  "is_coach",
                  "image_base64",
                  "image_address"]

    def get_image_address(self, obj):
        return obj.image.url if obj.image else None
