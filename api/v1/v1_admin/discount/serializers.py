from rest_framework import serializers

from course.models import Course
from discount_app.models import Coupon, Discount


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        exclude = ("is_deleted", "deleted_at")


class DiscountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Discount
        exclude = ("is_deleted", "deleted_at")


class DiscountListSerializer(serializers.Serializer):
    course = serializers.IntegerField()
    percent = serializers.IntegerField()
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()


class CreateDiscountSerializer(serializers.Serializer):
    discount = DiscountListSerializer(many=True)

    def create(self, validated_data):
        lst = []
        for i in validated_data.get("discount"):
            lst.append(Discount(
                percent=i["percent"],
                course_id=i["course"],
                start_date=i["start_date"],
                end_date=i["end_date"],
            ))

        if lst:
            discounts = Discount.objects.bulk_create(lst)
            return {
                "discount": [
                    {
                        "percent": d.percent,
                        "course": d.course.id if d.course else None,
                        "start_date": d.start_date,
                        "end_date": d.end_date,
                    }
                    for d in discounts
                ]
            }
        return {"discount": []}


class DiscountCourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ("id", "course_name")
