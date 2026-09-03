from rest_framework import serializers

from apps.core_app.models import Image


class ImageSerializer(serializers.ModelSerializer):
    image_url = serializers.CharField(source="image.url", read_only=True)

    class Meta:
        model = Image
        fields = (
            "id",
            "image",
            "image_url",
            "title",
            "file_size",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("file_size",)
