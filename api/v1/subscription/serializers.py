import json
from datetime import timedelta
from django.conf import settings
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers, exceptions
from django.utils.translation import gettext_lazy as _

from course.enums import PlanTypeEnum
from course.models import Course, CourseTypeModel
from discount_app.models import Coupon
from subscription_app.models import Subscription, PaymentSubscription, PaymentVerify
from utils.gateway import Zibal


class SubscriptionSerializer(serializers.ModelSerializer):
    course_name = serializers.SerializerMethodField()
    course_category_name = serializers.SerializerMethodField()
    user_full_name = serializers.SerializerMethodField()
    user_mobile_phone = serializers.SerializerMethodField()
    coupon_code = serializers.SerializerMethodField()

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

    def get_coupon_code(self, obj):
        return obj.coupon.code if obj.coupon else None


class CreateSubscriptionSerializer(serializers.ModelSerializer):
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.only("course_name"),
    )
    crud_course_type = serializers.PrimaryKeyRelatedField(
        queryset=CourseTypeModel.objects.only("course_type", "amount", "plan_type", "course_type")
    )

    class Meta:
        model = Subscription
        fields = ("id", "course", "user", "crud_course_type")
        read_only_fields = ("user",)

    def create(self, validated_data):
        user = self.context['request'].user
        plan_type = validated_data['crud_course_type'].plan_type
        day = validated_data['crud_course_type'].amount
        course_type = validated_data['crud_course_type']

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
        data.price = course_type.final_price
        data.save()
        return data


class SimpleSubscription(serializers.ModelSerializer):
    class Meta:
        model = Subscription
        fields = ("course", "price", "end_date", "status")


class PaymentSubscriptionSerializer(serializers.ModelSerializer):
    subscription = SimpleSubscription()

    class Meta:
        model = PaymentSubscription
        fields = ("subscription", "created_at", "response_payment")


class PaySubscriptionSerializer(serializers.ModelSerializer):
    subscription = serializers.PrimaryKeyRelatedField(
        queryset=Subscription.objects.only("status", "user__mobile_phone"),
    )
    coupon_code = serializers.CharField(required=False)

    class Meta:
        model = PaymentSubscription
        fields = ("subscription", "coupon_code")

    def validate(self, attrs):
        # print(attrs)
        # print(attrs.get("subscription").id)
        get_sub = Subscription.objects.filter(
            id=attrs['subscription'].id,
            status="pending",
            user_id=self.context['request'].user.id
        ).only(
            "user__mobile_phone",
            "user__email",
            "user__first_name",
            "user__last_name",
            "status"
        )

        if not get_sub.exists():
            raise exceptions.NotFound()
        attrs['get_sub'] = get_sub
        return attrs

    # def validate_coupon_code(self, data):
    #     if not Coupon.objects.filter(
    #             code=data,
    #             is_active=True,
    #             valid_from__lte=timezone.now(),
    #             valid_to__gte=timezone.now()
    #     ).exists():
    #         raise exceptions.ValidationError({"message": _("code is not exits or wrong")})
    #     return data

    def create(self, validated_data):
        # gateway merchant id
        zibal_api_key = settings.ZIBAL_MERCHENT_ID

        # get sub after validate
        get_sub = validated_data['get_sub']

        # get coupon_code
        coupon_code = validated_data.get('coupon_code', None)

        # validate coupon code
        coupon = Coupon.objects.filter(
                code=coupon_code,
                is_active=True,
                valid_from__lte=timezone.now(),
                valid_to__gte=timezone.now()
        ).only(
            "id",
            "discount"
        )

        # if coupon is existing we check coupon
        if coupon_code and not coupon.exists():
            raise exceptions.ValidationError({"message": _("code is not exits or wrong")})

        else:
            # check amount discount coupon
            if coupon and coupon.last().discount == 100:
                # create payment subscription
                data = {
                        "status": "success",
                        "message": "you successfully active subscription"
                }
                pay_sub = PaymentSubscription.objects.create(
                    subscription=get_sub.last(),
                    response_payment = data
                )
                # update status subscription
                get_sub.update(status="ACTIVE")
                # return data
                return pay_sub

            else:

                # create gateway
                instance = Zibal(
                    api_key=zibal_api_key,
                    call_back_url=settings.ZIBAL_CALLBACK_URL,
                    amount=int(get_sub.last().final_price_by_tax_coupon(coupon_code)),
                )

                # create payment subscription
                pay_sub = PaymentSubscription.objects.create(
                    subscription=get_sub.last()
                )
                pay_sub.response_payment = instance.request_url()
                pay_sub.save()
                return pay_sub

    def to_representation(self, instance):
        # if instance.response_payment
        return instance.response_payment


class PaymentVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = PaymentVerify
        fields = ("verify_payment", "created_at")
