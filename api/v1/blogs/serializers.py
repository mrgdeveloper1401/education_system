from rest_framework import serializers

from blog_app import models


class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CategoryBlog
        fields = ['id', "category_name", "category_slug"]


class ListBlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PostBlog
        fields = ["id", 'post_cover_image', "post_title", "created_at"]


class CreateBlogCommentSerialize(serializers.ModelSerializer):
    class Meta:
        model = models.CommentBlog
        fields = ['id', "comment_body"]
