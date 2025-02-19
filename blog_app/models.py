from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from django_ckeditor_5.fields import CKEditor5Field
from treebeard.mp_tree import MP_Node

from core.models import UpdateMixin, CreateMixin, SoftDeleteMixin


class CategoryBlog(MP_Node, CreateMixin, UpdateMixin, SoftDeleteMixin):
    category_name = models.CharField(max_length=255)
    category_slug = models.SlugField(max_length=255, allow_unicode=True)
    is_publish = models.BooleanField(default=True)

    def __str__(self):
        return self.category_name
    node_order_by = ["category_name"]


class PostBlog(CreateMixin, UpdateMixin, SoftDeleteMixin):
    author = models.ManyToManyField('accounts.User', related_name='post_authors')
    category = models.ForeignKey(CategoryBlog, on_delete=models.DO_NOTHING, related_name="blog_posts")
    post_introduction = models.CharField(max_length=255, help_text=_("مقدمه ای در مورد پست"))
    post_title = models.CharField(max_length=255, help_text=_("عنوان پست"))
    post_slug = models.SlugField(max_length=255, allow_unicode=True)
    post_body = CKEditor5Field(config_name='extends')
    read_count = models.PositiveIntegerField(default=0, help_text=_("چند نفر این پست را دیده اند"))
    read_time = models.PositiveSmallIntegerField(help_text=_("مدت زمان برای مطالعه این مقاله"))
    post_cover_image = models.ImageField(upload_to="blog/%Y/%m/%d")
    tags = models.ManyToManyField("TagBlog", blank=True, related_name="post_tags")
    likes = models.PositiveIntegerField(default=0)
    is_publish = models.BooleanField(default=True)

    def __str__(self):
        return self.post_title


class TagBlog(CreateMixin, UpdateMixin, SoftDeleteMixin):
    tag_name = models.CharField(max_length=255)
    is_publish = models.BooleanField(default=True)

    def __str__(self):
        return self.tag_name

    class Meta:
        db_table = 'blog_tag'


class FavouritePost(CreateMixin, UpdateMixin, SoftDeleteMixin):
    user = models.ForeignKey("accounts.User", on_delete=models.DO_NOTHING, related_name="favourite_user_posts")
    post = models.ForeignKey(PostBlog, on_delete=models.DO_NOTHING, related_name="favourite_posts")

    class Meta:
        db_table = 'blog_favourite_post'
        ordering = ['-created_at']


class CommentBlog(CreateMixin, UpdateMixin, SoftDeleteMixin):
    user = models.ForeignKey("accounts.User", on_delete=models.DO_NOTHING, related_name="comment_user_posts")
    post = models.ForeignKey(PostBlog, on_delete=models.DO_NOTHING, related_name="comment_posts")
    comment_body = models.TextField()
    reply = models.ForeignKey("self", on_delete=models.DO_NOTHING, related_name="replies", blank=True, null=True)
    is_publish = models.BooleanField(default=True)

    class Meta:
        db_table = 'blog_comment'
        ordering = ['-created_at']
