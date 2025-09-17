from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory
from django.utils.translation import gettext_lazy as _

from . import models


class CategoryAdmin(TreeAdmin, ImportExportModelAdmin):
    list_display = ('category_name', "id", 'category_slug', "is_publish")
    prepopulated_fields = {'category_slug': ('category_name',)}
    search_fields = ('category_name',)
    list_filter = ('is_publish', "created_at")
    list_per_page = 20
    form = movenodeform_factory(models.CategoryBlog)

    def get_queryset(self, request):
        return super().get_queryset(request).defer(
            "is_deleted",
            "deleted_at"
        )


class BlogPostAdmin(admin.ModelAdmin):
    raw_id_fields = ('category',)
    list_display = ('category', "post_title", "is_publish", "created_at")
    filter_horizontal = ('tags', "author")
    list_select_related = ("category",)
    list_per_page = 20
    search_fields = ("post_title",)
    list_filter = ("is_publish",)

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related("tags", "author").only(
            "author__mobile_phone",
            "tags__tag_name",
            "category__category_name",
            "created_at",
            "updated_at",
            "read_count",
            "post_introduction",
            "post_title",
            "post_slug",
            "post_body",
            "read_time",
            "post_cover_image",
            "likes",
            "is_publish",
            "description_slug",
            "is_publish"
        )


@admin.register(models.Like)
class LikeAdmin(admin.ModelAdmin):
    raw_id_fields = ("user", "post")
    list_select_related = ("user", "post")
    list_per_page = 20
    search_fields = ("user__mobile_phone", "post__post_title")
    search_help_text = _("برای جست و جو میتوانید از شماره موبایل یا عنوان پست بلاگ استفاده کنید")
    list_display = ("user", "post", "created_at")

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "created_at",
            "user__mobile_phone",
            "post__post_title"
        )


@admin.register(models.TagBlog)
class TagBlogAdmin(admin.ModelAdmin):
    list_display = ("id", "tag_name", "is_publish")


admin.site.register(models.CategoryBlog, CategoryAdmin)
admin.site.register(models.PostBlog, BlogPostAdmin)
