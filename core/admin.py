from django.contrib import admin

from .models import SitemapEntry, CourseSiteInformation


@admin.register(SitemapEntry)
class SitemapEntryAdmin(admin.ModelAdmin):
    list_display = ("id", "last_modified", "priority")
    list_per_page = 20

    def get_queryset(self, request):
        return super().get_queryset(request).defer(
            "is_deleted",
            "deleted_at",
        )


@admin.register(CourseSiteInformation)
class CourseSiteInformationAdmin(admin.ModelAdmin):
    list_display = (
        "class_counter",
        "task_counter",
        "user_counter",
        "video_counter",
        "created_at",
        "updated_at",
        "id"
    )
    list_per_page = 20

    def get_queryset(self, request):
        return super().get_queryset(request).defer(
            "is_deleted",
            "deleted_at",
        )
