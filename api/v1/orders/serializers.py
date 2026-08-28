from decouple import config
from django.core.cache import cache
from rest_framework import serializers, exceptions

from apps.account_app.tasks import send_otp_sms_task
from apps.account_app.models import User
from apps.course_app.models import Course
from apps.order_app.models import Order, CourseSignUp
from apps.order_app.tasks import send_successfully_signup_task, process_referral
from base.utils.config import generate_otp_code, get_client_ip


# TODO, move into config file
OTP_TEMPLATE_ID = config("SMS_IR_OTP_TEMPLATE_ID", cast=int)
COURSE_SIGNUP_TEMPLATE_ID = config("SMS_IR_COURSE_SIGNUP_TEMPLATE_ID", cast=int)

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("course", "price", "mobile_phone")


class CourseSignUpSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.only("course_name")
    )
    referral_code = serializers.CharField(required=False)

    class Meta:
        model = CourseSignUp
        fields = ("course", "mobile_phone", "first_name", "last_name", "have_account", "referral_code")
        read_only_fields = ("have_account",)

    def validate(self, attrs):
        mobile_phone = attrs.get("mobile_phone")

        # check register user in course_signup
        if CourseSignUp.objects.filter(mobile_phone=mobile_phone).exists():
            raise exceptions.ValidationError("you have already registered")
        return attrs

    def create(self, validated_data):
        # get referral_code
        referral_code = validated_data.pop("referral_code", None)

        # get data mobile_phone
        mobile_phone = validated_data['mobile_phone']

        # get user
        get_user = User.objects.filter(mobile_phone=mobile_phone).only("mobile_phone", "first_name", "last_name")
        # check user exits
        if not get_user.exists():

            # create user
            user = User.objects.create_user(
                mobile_phone=mobile_phone,
                password=mobile_phone,
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
            )

            # send sms (phone and password) for cussedly signup
            send_successfully_signup_task.delay(
                phone=user.mobile_phone,
                template_id=COURSE_SIGNUP_TEMPLATE_ID,
                template_name='course_signup',
                password=user.mobile_phone,
                full_name=user.get_full_name
            )

        else:
            # generate code
            code = generate_otp_code()
            user_ip = get_client_ip(self.context['request'])
            cache_key = f'otp_{get_user.mobile_phone}_{code}_{user_ip}'
            cache.set(cache_key, code, timeout=120)

            # send sms otp
            send_otp_sms_task.delay(get_user.mobile_phone, code, 'otp', OTP_TEMPLATE_ID)

        # if referral_code is exiting, do task
        if referral_code:
            process_referral.delay(
                referral_code=referral_code,
                mobile_phone=mobile_phone
            )

        # return data
        return CourseSignUp.objects.create(**validated_data)
