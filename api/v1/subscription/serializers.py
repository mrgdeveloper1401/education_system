from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from accounts.models import User
from subscription_app.models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        exclude = ['created_at', "updated_at", "deleted_at", "is_deleted", "is_active", "user"]
        extra_kwargs = {
            "status": {"read_only": True},
        }


class CreateSubscriptionSerializer(serializers.ModelSerializer):
    user = serializers.CharField()

    class Meta:
        model = Subscription
        exclude = ['created_at', "updated_at", "deleted_at", "is_deleted", "is_active", "status"]

    def validate(self, attrs):
        user = attrs.get("user")
        subscription = Subscription.objects.filter(user__mobile_phone=user).last()
        if subscription and (subscription.status == 'active' or subscription.status == "waiting"):
            raise serializers.ValidationError("you have already subscription")
        return attrs

    def create(self, validated_data):
        user_mobile_phone = validated_data.pop("user")
        user = get_object_or_404(User, mobile_phone=user_mobile_phone)
        return Subscription.objects.create(user=user, **validated_data)


class UpdateSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        exclude = ['created_at', "updated_at", "deleted_at", "is_deleted", "is_active", "user"]
        extra_kwargs = {
            "status": {"read_only": True},
        }

    def validate(self, attrs):
        start_date = attrs.get("start_date")
        end_date = attrs.get("end_date")
        user = self.context['user']
        subscription = Subscription.objects.get(user=user)

        if start_date and end_date:
            if start_date > end_date:
                raise serializers.ValidationError("start_date must be less than end_date")
        if start_date:
            if start_date > subscription.end_date:
                raise serializers.ValidationError("start_date must be less than subscription.end_date")
        if end_date:
            if end_date < subscription.start_date:
                raise serializers.ValidationError("end_date must be greater than subscription.start_date")
        return attrs
