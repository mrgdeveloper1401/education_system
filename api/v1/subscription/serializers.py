from rest_framework import serializers

from subscription_app.models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    course_name = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        exclude = ("is_deleted", "deleted_at", "user")

    def get_course_name(self, obj):
        return obj.course.course_name
