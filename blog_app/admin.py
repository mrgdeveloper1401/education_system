from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from . import models

# Register your models here.


class CategoryAdmin(TreeAdmin, ImportExportModelAdmin):
    list_display = ('category_name', "id", 'category_slug', "is_publish")
    prepopulated_fields = {'category_slug': ('category_name',)}
    search_fields = ['category_name']
    list_filter = ['is_publish', "created_at"]
    list_per_page = 20
    form = movenodeform_factory(models.CategoryBlog)


class BlogPostAdmin(admin.ModelAdmin):
    raw_id_fields = ['category']
    list_display = ['category', "post_title", "is_publish", "created_at"]
    prepopulated_fields = {"post_slug": ("post_title",)}
    filter_horizontal = ['tags', "author"]


admin.site.register(models.CategoryBlog, CategoryAdmin)
admin.site.register(models.PostBlog, BlogPostAdmin)
admin.site.register(models.TagBlog)