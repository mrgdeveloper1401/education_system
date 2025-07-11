from rest_framework import serializers

from core.models import SitemapEntry, CourseSiteInformation


class SiteMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = SitemapEntry
        fields = (
            "id",
            "slug_text",
            "last_modified",
            "changefreq",
            "priority"
        )


class CourseSiteInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseSiteInformation
        exclude = (
            "is_deleted",
            "deleted_at",
            "created_at",
            "updated_at"
        )
