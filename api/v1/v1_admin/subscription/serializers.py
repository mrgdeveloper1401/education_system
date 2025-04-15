from drf_spectacular.utils import extend_schema, extend_schema_field
from rest_framework import serializers

from accounts.models import User
from subscription_app.models import Subscription, Plan


class PlanSerializer(serializers.ModelSerializer):
    final_price = serializers.SerializerMethodField()
    calc_discount_value = serializers.SerializerMethodField()

    class Meta:
        model = Plan
        exclude = ("is_deleted", "deleted_at")

    @extend_schema_field(serializers.IntegerField())
    def get_final_price(self, obj):
        return obj.final_price

    @extend_schema_field(serializers.IntegerField())
    def get_calc_discount_value(self, obj):
        return obj.calc_discount


class SubscriptionSerializer(serializers.ModelSerializer):
    # plan = PlanSerializer(read_only=True)
    # plan_id = serializers.PrimaryKeyRelatedField(
    #     queryset=Plan.objects.all(),
    #     source='plan',
    #     write_only=True
    # )
    remaining_days = serializers.SerializerMethodField()
    # status_display = serializers.SerializerMethodField()
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(is_active=True).only("mobile_phone"),
    )
    plan = serializers.PrimaryKeyRelatedField(
        queryset=Plan.objects.filter(is_active=True).only("plan_title"),
    )

    class Meta:
        model = Subscription
        fields = [
            'id', 'user', 'plan', 'plan_id', 'end_date', 'is_active', 'status', 'remaining_days',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'status']

    def get_remaining_days(self, obj):
        return obj.remaining_days

    # def get_status_display(self, obj):
    #     return obj.get_status_display()