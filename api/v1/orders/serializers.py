from rest_framework import serializers, exceptions

from accounts.models import User
from course.models import Course
from order_app.models import Order, CourseSignUp


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("course", "price", "mobile_phone")


class CourseSignUpSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.only("course_name")
    )

    class Meta:
        model = CourseSignUp
        fields = ("course", "mobile_phone", "first_name", "last_name", "have_account")
        read_only_fields = ("have_account",)

    def validate(self, attrs):
        mobile_phone = attrs.get("mobile_phone")

        if CourseSignUp.objects.filter(mobile_phone=mobile_phone).exists():
            raise exceptions.ValidationError("you have already registered")
        return attrs


# class PaymentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Payment
#         exclude = ("is_deleted", "deleted_at")
