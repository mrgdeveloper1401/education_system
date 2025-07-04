import datetime
import random
import string

from django.utils import timezone
from rest_framework import serializers, exceptions

from accounts.models import User, Otp, Student, Invitation, PrivateNotification
from course.models import Course
from discount_app.models import Coupon
from order_app.models import Order, CourseSignUp
from order_app.tasks import send_successfully_signup, process_referral
from accounts.tasks import send_sms_otp_code


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
        get_user = User.objects.filter(mobile_phone=mobile_phone).only("mobile_phone")

        # check user exits
        if not get_user.exists():

            # create user
            user = User.objects.create_user(
                mobile_phone=mobile_phone,
                password=mobile_phone,
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
            )

            # send sms (phone and password) for seccussfly signup
            send_successfully_signup.delay(
                phone=user.mobile_phone,
                password=user.mobile_phone,
                full_name=user.get_full_name,
            )

        else:
            # create otp
            otp = Otp.objects.create(
                mobile_phone=mobile_phone
            )

            # send sms otp
            send_sms_otp_code.delay(otp.mobile_phone, otp.code)

        # if referral_code is exiting, do task
        if referral_code:
            process_referral.delay(
                referral_code=referral_code,
                mobile_phone=mobile_phone
            )

        # return data
        return CourseSignUp.objects.create(**validated_data)
