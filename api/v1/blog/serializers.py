from rest_framework import serializers
from blog_app.models import CategoryBlog, PostBlog, TagBlog, FavouritePost, CommentBlog
from api.v1.user.serializers import UserSerializer


class CategoryBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryBlog
        exclude = ("is_deleted", "deleted_at")


class TagBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagBlog
        exclude = ("is_deleted", "deleted_at")


class PostBlogSerializer(serializers.ModelSerializer):
    author = UserSerializer(many=True, read_only=True)
    category = CategoryBlogSerializer(read_only=True)
    tags = TagBlogSerializer(many=True, read_only=True)

    class Meta:
        model = PostBlog
        exclude = ("is_deleted", "deleted_at")
        read_only_fields = ('read_count', 'likes')


class FavouritePostSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    post = PostBlogSerializer(read_only=True)

    class Meta:
        model = FavouritePost
        exclude = ("is_deleted", "deleted_at")


class CommentBlogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()

    class Meta:
        model = CommentBlog
        exclude = ("is_deleted", "deleted_at")

    def get_replies(self, obj):
        replies = obj.replies.filter(is_publish=True)
        serializer = CommentBlogSerializer(replies, many=True)
        return serializer.data
