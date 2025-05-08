from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType

from discount_app.models import Discount


class DiscountSerializer(serializers.ModelSerializer):
    content_type = serializers.SlugRelatedField(
        queryset=ContentType.objects.all(),
        slug_field='model'
    )

    class Meta:
        model = Discount
        exclude = ("is_deleted", "deleted_at")

    def validate(self, data):
        content_type = data.get('content_type')
        object_id = data.get('object_id')

        if content_type and object_id:
            model_class = content_type.model_class()
            if not model_class.objects.filter(pk=object_id).exists():
                raise serializers.ValidationError(
                    {"object_id": "آیتم مورد نظر یافت نشد"}
                )

        return data
