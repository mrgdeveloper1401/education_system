from django.contrib import admin

from . import models


@admin.register(models.Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("title", "file", "is_publish", "created_at", "updated_at")
    search_fields = ("title",)
    list_editable = ("is_publish",)
    list_per_page = 20

    def get_queryset(self, request):
        return super().get_queryset(request).defer("is_deleted", "deleted_at")
