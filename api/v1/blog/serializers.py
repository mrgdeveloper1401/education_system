from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from accounts.models import User
from blog_app.models import CategoryBlog, PostBlog, TagBlog, FavouritePost, CommentBlog
from api.v1.user.serializers import UserSerializer


# list and retrieve category blog serializer
class CategoryBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryBlog
        exclude = ("is_deleted", "deleted_at")


# create category
class CreateCategorySerializer(serializers.ModelSerializer):
    parent = serializers.IntegerField(required=False)

    class Meta:
        model = CategoryBlog
        fields = ("category_name", "parent", "description_slug", "description")

    def create(self, validated_data):
        parent = validated_data.pop("parent", None)

        if parent is None:
            return CategoryBlog.add_root(**validated_data)
        else:
            category = get_object_or_404(CategoryBlog, pk=parent)
            return category.add_child(**validated_data)


class TagBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagBlog
        exclude = ("is_deleted", "deleted_at")


class FullNameAuthorPostBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("get_full_name",)


class TagPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagBlog
        fields = ("id", "tag_name")


class PostBlogSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()

    class Meta:
        model = PostBlog
        exclude = ("is_deleted", "deleted_at", "category")
        read_only_fields = ('read_count', 'likes')

    def get_category_name(self, obj):
        return obj.category.category_name

    def create(self, validated_data):
        category_id = self.context['category_pk']
        author = validated_data.pop("author", None)
        tags = validated_data.pop("tags", None)
        post_blog =  PostBlog.objects.create(category_id=category_id, **validated_data)
        post_blog.author.set(author)
        post_blog.tags.set(tags)
        return post_blog

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['author'] = FullNameAuthorPostBlogSerializer(instance.author, many=True).data
        data['tags'] = TagPostSerializer(instance.tags, many=True).data
        return data


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
        exclude = ("is_deleted", "deleted_at", "post")

    def get_replies(self, obj):
        replies = obj.replies.filter(is_publish=True)
        serializer = CommentBlogSerializer(replies, many=True)
        return serializer.data

    def create(self, validated_data):
        user = self.context['request'].user
        post_id = self.context['post_pk']
        return CommentBlog.objects.create(user=user, post_id=post_id, **validated_data)


class AuthorListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "get_full_name",
            "mobile_phone",
            "id"
        )


class LatestPostSerializer(serializers.ModelSerializer):
    author = FullNameAuthorPostBlogSerializer(many=True)

    class Meta:
        model = PostBlog
        fields = (
            "id",
            "category_id",
            "post_title",
            "post_introduction",
            "author",
            "post_cover_image",
            "post_slug",
            "created_at",
            "updated_at"
        )


class LikePostBlogSerializer(serializers.Serializer):
    pass
