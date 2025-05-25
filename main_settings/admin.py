from django.contrib import admin

from . import models


@admin.register(models.Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "file", "is_publish", "created_at", "banner_type", "updated_at")
    search_fields = ("title",)
    list_editable = ("is_publish", 'banner_type')
    list_per_page = 20

    def get_queryset(self, request):
        return super().get_queryset(request).defer("is_deleted", "deleted_at")


@admin.register(models.HeaderSite)
class HeaderSiteAdmin(admin.ModelAdmin):
    list_display = ("header_title", "text_color", "background_color", "is_publish", "created_at")
    list_per_page = 20
    list_filter = ("is_publish",)
    list_editable = ("is_publish",)

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "created_at",
            "background_color",
            "text_color",
            "is_publish",
            "header_title",
            "image"
        )
