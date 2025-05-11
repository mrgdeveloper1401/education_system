from datetime import timedelta

from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from course.enums import PlanTypeEnum
from course.models import Course, CourseTypeModel
from subscription_app.models import Subscription


class SubscriptionSerializer(serializers.ModelSerializer):
    course_name = serializers.SerializerMethodField()
    course_category_name = serializers.SerializerMethodField()
    user_full_name = serializers.SerializerMethodField()
    user_mobile_phone = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        exclude = ("is_deleted", "deleted_at", "user", "course")


    def get_course_name(self, obj):
        return obj.course.course_name

    @extend_schema_field(serializers.IntegerField())
    def get_course_category_name(self, obj):
        return obj.course.category.category_name

    def get_user_full_name(self, obj):
        return obj.user.get_full_name

    def get_user_mobile_phone(self, obj):
        return obj.user.mobile_phone


class CreateSubscriptionSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.only("course_name"),
    )
    crud_course_type = serializers.PrimaryKeyRelatedField(
        queryset=CourseTypeModel.objects.only("course_type", "amount", "plan_type", "course_type")
    )

    class Meta:
        model = Subscription
        fields = ("course", "user", "crud_course_type")
        read_only_fields = ("user",)

    def create(self, validated_data):
        user = self.context['request'].user
        plan_type = validated_data['crud_course_type'].plan_type
        day = validated_data['crud_course_type'].amount

        end_date = timezone.now()

        if plan_type == PlanTypeEnum.month:
            end_date += timedelta(days=day * 30)
        elif plan_type == PlanTypeEnum.year:
            end_date += timedelta(days=day * 365)
        else:
            end_date += timedelta(days=day)

        data = Subscription.objects.create(
            user=user,
            end_date=end_date,
            **validated_data
        )
        return data
