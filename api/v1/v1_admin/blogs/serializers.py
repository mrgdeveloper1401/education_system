from rest_framework import serializers
from rest_framework import generics
from django.utils.translation import gettext_lazy as _

from blog_app.models import CategoryBlog, PostBlog, TagBlog, CommentBlog, FavouritePost


class AdminCreateCategoryBlogSerializer(serializers.ModelSerializer):
    parent = serializers.IntegerField(required=False)

    class Meta:
        model = CategoryBlog
        fields = ['category_name', "parent"]

    def create(self, validated_data):
        parent = validated_data.pop("parent", None)
        if parent:
            instance = generics.get_object_or_404(CategoryBlog, pk=parent)
            instance.add_child(**validated_data)
        else:
            instance = CategoryBlog.add_root(**validated_data)
        return instance


class AdminListCategoryBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryBlog
        fields = ['id', "category_name", "category_slug", "is_publish", "created_at", "updated_at"]


class AdminCreatePostBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostBlog
        exclude = ['deleted_at', "is_deleted", "read_count", "likes"]
        extra_kwargs = {
            "post_slug": {"required": False},
        }


class AdminRetrievePostBlogSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        many=True, slug_field="mobile_phone", read_only=True
    )
    tags = serializers.SlugRelatedField(
        many=True, slug_field="tag_name", read_only=True
    )

    class Meta:
        model = PostBlog
        exclude = ['deleted_at', "is_deleted"]


class AdminListPostBlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = PostBlog
        fields = ['id', "post_title", "post_slug", "post_cover_image", "created_at"]


class AdminCreateTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagBlog
        fields = ['tag_name']


class AdminListTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagBlog
        fields = ['id', "tag_name", 'is_publish']


class AdminUpdateTagsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TagBlog
        exclude = ['is_deleted', "deleted_at"]


class AdminCreateFavouritePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavouritePost
        fields = ['user', "post"]

    def validate(self, attrs):
        if FavouritePost.objects.filter(user_id=attrs["user"].id, post_id=attrs['post'].id).exists():
            raise serializers.ValidationError({"message": _("you already these adding into post to favorite")})
        return attrs


class AdminListFavouritePostSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(read_only=True, slug_field="mobile_phone")
    post = serializers.SlugRelatedField(read_only=True, slug_field="post_title")

    class Meta:
        model = FavouritePost
        fields = ["id", 'user', "post"]


class AdminUpdateFavouritePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = FavouritePost
        exclude = ['is_deleted', "deleted_at"]


class AdminListCommentSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="mobile_phone", read_only=True)
    post = serializers.SlugRelatedField(slug_field="post_title", read_only=True)

    class Meta:
        model = CommentBlog
        fields = ['id', "user", "post", "is_publish", "created_at"]


class AdminUpdateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentBlog
        exclude = ['is_deleted', "deleted_at"]


class AdminCreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommentBlog
        fields = ['user', "post", "comment_body", "is_publish"]
