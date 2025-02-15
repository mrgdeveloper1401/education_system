from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from . import models

# Register your models here.


class CategoryAdmin(ImportExportModelAdmin):
    list_display = ('category_name', "id", 'category_slug', "is_publish", "parent")
    raw_id_fields = ['parent']
    prepopulated_fields = {'category_slug': ('category_name',)}
    list_select_related = ['parent']
    search_fields = ['category_name']
    list_filter = ['is_publish', "created_at"]
    list_per_page = 20


class BlogPostAdmin(admin.ModelAdmin):
    raw_id_fields = ['category']
    list_display = ['category', "post_title", "is_publish", "created_at"]
    prepopulated_fields = {"post_slug": ("post_title",)}
    filter_horizontal = ['tags', "author"]


admin.site.register(models.CategoryBlog, CategoryAdmin)
admin.site.register(models.PostBlog, BlogPostAdmin)
