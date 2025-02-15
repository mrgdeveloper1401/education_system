from rest_framework import viewsets
from rest_framework import permissions

from . import serializers
from blog_app.models import CategoryBlog, PostBlog


class BlogCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.BlogCategorySerializer
    queryset = CategoryBlog.objects.filter(is_publish=True).only(
        "id", "category_name", "category_slug"
    )


class BlogPostViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ListBlogPostSerializer

    def get_queryset(self):
        if self.action == "list":
            return PostBlog.objects.filter(category_id=self.kwargs["category_pk"]).only(
                "id", "post_title", "post_cover_image", "created_at"
            )


class BlogCommentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CreateBlogCommentSerialize
    permission_classes = [permissions.IsAuthenticated]
    queryset = PostBlog.objects.filter(is_publish=True)
