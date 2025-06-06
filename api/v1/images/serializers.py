from rest_framework import serializers

from images.models import Image


class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ("id", "image", "image_url", "title", "file_size", "created_at", "updated_at")
        read_only_fields = ("file_size",)
