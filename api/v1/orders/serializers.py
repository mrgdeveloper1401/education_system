from rest_framework import serializers, exceptions

from accounts.models import Student, Invitation
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
    referral_code = serializers.CharField(required=False)

    class Meta:
        model = CourseSignUp
        fields = ("course", "mobile_phone", "first_name", "last_name", "have_account", "referral_code")
        read_only_fields = ("have_account",)

    def validate(self, attrs):
        mobile_phone = attrs.get("mobile_phone")

        if CourseSignUp.objects.filter(mobile_phone=mobile_phone).exists():
            raise exceptions.ValidationError("you have already registered")

        # get referral code in data
        # referral_code = attrs.get("referral_code", None)

        # check referral code is existing?
        # if referral_code:
            # get
            # student = Student.objects.filter(
            #     referral_code=referral_code
            # ).only(
            #     "student_number"
            # )

            # if student:
            #     Invitation.objects.create(
            #         from_student=student,
            #         to_student=
            #     )
        return attrs


# class PaymentSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Payment
#         exclude = ("is_deleted", "deleted_at")
