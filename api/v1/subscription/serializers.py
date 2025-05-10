from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from course.models import Course, CourseTypeModel
from subscription_app.models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    course_name = serializers.SerializerMethodField()
    course_category_name = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        exclude = ("is_deleted", "deleted_at", "mobile_phone")

    def get_course_name(self, obj):
        return obj.course.course_name

    @extend_schema_field(serializers.IntegerField())
    def get_course_category_name(self, obj):
        return obj.course.category.category_name


class CreateSubscriptionSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.only("course_name"),
    )
    crud_course_type = serializers.PrimaryKeyRelatedField(
        queryset=CourseTypeModel.objects.only("course_type")
    )

    class Meta:
        model = Subscription
        fields = ("course", "mobile_phone", "start_date", "price", "crud_course_type")
