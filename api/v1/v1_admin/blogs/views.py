from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from . import serializers
from blog_app.models import CategoryBlog, PostBlog, TagBlog, FavouritePost, CommentBlog


class AdminCategoryBlogViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.AdminCreateCategoryBlogSerializer
        else:
            return serializers.AdminListCategoryBlogSerializer

    def get_queryset(self):
        return CategoryBlog.objects.all().only(
            'id', "category_name", "category_slug", "is_publish", "created_at", "updated_at"
        )


class AdminBlogPostViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return serializers.AdminCreatePostBlogSerializer
        if self.action == "list":
            return serializers.AdminListPostBlogSerializer
        else:
            return serializers.AdminRetrievePostBlogSerializer

    def get_queryset(self):
        if self.action == "list":
            return PostBlog.objects.all().only('id', "post_title", "post_cover_image", "created_at", "post_slug")
        return PostBlog.objects.all().defer("is_deleted", "deleted_at").prefetch_related(
            "author", "tags"
        )


class AdminTagViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.AdminCreateTagsSerializer
        if self.action == "list":
            return serializers.AdminListTagSerializer
        else:
            return serializers.AdminUpdateTagsSerializer

    def get_queryset(self):
        if self.action == "list":
            return TagBlog.objects.all().only("id", "tag_name", "is_publish")
        else:
            return TagBlog.objects.all().defer("is_deleted", "deleted_at")


class AdminFavoriteViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.AdminCreateFavouritePostSerializer
        if self.action == "list":
            return serializers.AdminListFavouritePostSerializer
        else:
            return serializers.AdminUpdateFavouritePostSerializer

    def get_queryset(self):
        if self.action == "list":
            return FavouritePost.objects.all().only("id", "user_id", "post_id").select_related("user", "post")
        else:
            return FavouritePost.objects.all().defer("is_deleted", "deleted_at")


class AdminCommentViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAdminUser,)

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.AdminListCommentSerializer
        if self.action == "create":
            return serializers.AdminCreateCommentSerializer
        else:
            return serializers.AdminUpdateCommentSerializer

    def get_queryset(self):
        if self.action == "list":
            return CommentBlog.objects.all().only('id', "user", "post", "is_publish", "created_at").select_related(
                "user", "post"
            )
        else:
            return CommentBlog.objects.all().defer("is_deleted", "deleted_at")
