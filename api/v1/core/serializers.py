from rest_framework import serializers


from core.models import SitemapEntry


class SiteMapSerializer(serializers.ModelSerializer):
    class Meta:
        model = SitemapEntry
        fields = (
            "slug_text",
            "last_modified",
            "changefreq",
            "priority"
        )
