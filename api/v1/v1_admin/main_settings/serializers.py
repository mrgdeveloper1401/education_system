from rest_framework import serializers

from main_settings.models import Banner, HeaderSite


class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ("id", "title", "is_publish", "file", "banner_type", "created_at")


class HeaderSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = HeaderSite
        fields = ("id", "header_title", "image", "background_color", "text_color")
