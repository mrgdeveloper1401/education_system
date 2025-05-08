from rest_framework import serializers, exceptions

from order_app.models import Order, CourseSignUp, Payment


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("course", "price", "mobile_phone")


class CourseSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSignUp
        fields = ("course", "mobile_phone", "fist_name", "last_name")

    def validate(self, attrs):
        if CourseSignUp.objects.filter(mobile_phone=attrs["mobile_phone"]).exists():
            raise exceptions.ValidationError("you have already registered")
        return attrs


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        exclude = ("is_deleted", "deleted_at")
