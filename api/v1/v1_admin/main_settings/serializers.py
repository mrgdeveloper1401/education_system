from rest_framework import serializers

from main_settings.models import Banner

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ("id", "title", "is_publish", "file", "banner_type", "created_at")
