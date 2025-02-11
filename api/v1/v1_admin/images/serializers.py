from rest_framework import serializers

from images.models import Image


class AdminCreateUpdateImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['title', "image"]


class AdminImageUpdateRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        exclude = ['is_deleted', "deleted_at"]


class AdminImageListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ["id", 'title', "image"]
