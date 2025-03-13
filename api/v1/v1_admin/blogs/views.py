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
        return CategoryBlog.objects.only(
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
        query = PostBlog.objects.filter(category_id=self.kwargs["category_pk"])
        if self.action == "list":
            query = query.only('id', "post_title", "post_cover_image", "created_at", "post_slug")
        else:
            query = query.defer("is_deleted", "deleted_at").prefetch_related(
                "author", "tags"
            )
        return query


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
        query = TagBlog.objects.all()
        if self.action == "list":
            query = query.only("id", "tag_name", "is_publish")
        else:
            query = query.defer("is_deleted", "deleted_at")
        return query


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
        query = FavouritePost.objects.all()
        if self.action == "list":
            query = query.only("id", "user_id", "post_id").select_related("user", "post")
        else:
            query = query.defer("is_deleted", "deleted_at")
        return query


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
        query = CommentBlog.objects.filter(post_id=self.kwargs["post_pk"])
        if self.action == "list":
            query = query.only('id', "user", "post", "is_publish", "created_at").select_related(
                "user", "post"
            )
        else:
            query = query.defer("is_deleted", "deleted_at")
        return query
