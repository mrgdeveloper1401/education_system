from django.contrib import admin

from .models import Image
# Register your models here.


@admin.register(Image)
class ImageAdmin(admin.ModelAdmin):
    list_display = ['image', "title", 'file_size', "created_at", "updated_at", "deleted_at", "is_deleted"]
    search_fields = ['title']
    readonly_fields = ['deleted_at', "is_deleted"]
    list_display_links = ['image', "title"]