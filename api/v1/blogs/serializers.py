from rest_framework import serializers

from blog_app import models


class BlogCategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = models.CategoryBlog
        fields = ['id', "category_name", "category_slug", "children"]

    def get_children(self, obj):
        return BlogCategorySerializer(obj.get_children(), many=True).data


class BlogCategoryRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CategoryBlog
        fields = ['id', "category_name", "category_slug"]


class ListBlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PostBlog
        fields = ["id", 'post_cover_image', "post_title", "created_at"]


class RetrieveBlogPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PostBlog
        exclude = ['deleted_at', "is_deleted"]


class CreateBlogCommentSerialize(serializers.ModelSerializer):
    class Meta:
        model = models.CommentBlog
        fields = ['id', "comment_body"]
