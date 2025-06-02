from django.contrib import admin

from .models import Image
# Register your models here.


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ("title", 'file_size', "created_at", "updated_at",)
    search_fields = ('title',)
    list_display_links = ("title",)
    list_per_page = 20

    def get_queryset(self, request):
        return super().get_queryset(request).defer(
            "is_deleted",
            "deleted_at"
        )
