from django.contrib import admin

from .models import SitemapEntry
# Register your models here.


@admin.register(SitemapEntry)
class SitemapEntryAdmin(admin.ModelAdmin):
    list_display = ("last_modified", "priority")
    list_per_page = 20
    list_filter = ("last_modified",)

    def get_queryset(self, request):
        return super().get_queryset(request).defer(
            "is_deleted",
            "deleted_at",
        )
