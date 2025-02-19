from rest_framework import viewsets
from rest_framework import permissions
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator

from . import serializers
from blog_app.models import CategoryBlog, PostBlog
from .paginations import BlogPostPagination


class BlogCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.BlogCategorySerializer
    queryset = CategoryBlog.objects.filter(is_publish=True, depth=1).only(
        "id", "category_name", "category_slug", "numchild"
    )

    @method_decorator(cache_page(750, key_prefix='category_list_cache'))
    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, *kwargs)
        return response

    @method_decorator(cache_page(750, key_prefix='category_retrieve_cache'))
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        return response

    def get_queryset(self):
        query = CategoryBlog.objects.only("id", "category_name", "category_slug", "numchild")
        if self.action == "list":
            q = query.filter(is_publish=True, depth=1)
        else:
            q = query.filter(is_publish=True)
        return q

    def get_serializer_class(self):
        if self.action == "retrieve":
            return serializers.BlogCategoryRetrieveSerializer
        return super().get_serializer_class()


class BlogPostViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = BlogPostPagination

    def get_queryset(self):
        if self.action == "list":
            return PostBlog.objects.filter(category_id=self.kwargs["category_pk"]).only(
                "id", "post_title", "post_cover_image", "created_at"
            )
        else:
            return PostBlog.objects.filter(category_id=self.kwargs["category_pk"]).defer('deleted_at', "is_deleted")

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.ListBlogPostSerializer
        else:
            return serializers.RetrieveBlogPostSerializer


class BlogCommentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CreateBlogCommentSerialize
    permission_classes = [permissions.IsAuthenticated]
    queryset = PostBlog.objects.filter(is_publish=True)
