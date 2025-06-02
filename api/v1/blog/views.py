from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from blog_app.models import CategoryBlog, PostBlog, TagBlog, FavouritePost, CommentBlog
from utils.pagination import CommonPagination
from .serializers import (
    CategoryBlogSerializer,
    PostBlogSerializer,
    TagBlogSerializer,
    FavouritePostSerializer,
    CommentBlogSerializer,
    CreateCategorySerializer
)


class CategoryBlogViewSet(viewsets.ModelViewSet):
    queryset = CategoryBlog.objects.filter(is_publish=True).defer("is_deleted", "deleted_at")
    serializer_class = CategoryBlogSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            self.permission_classes =  (permissions.AllowAny,)
        else:
            self.permission_classes = (permissions.IsAdminUser,)
        return super().get_permissions()

    def filter_queryset(self, queryset):
        name = self.request.query_params.get("name", None)

        if name:
            return queryset.filter(category_name__icontains=name)
        else:
            return queryset

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateCategorySerializer
        else:
            return super().get_serializer_class()


class TagBlogViewSet(viewsets.ModelViewSet):
    queryset = TagBlog.objects.filter(is_publish=True)
    serializer_class = TagBlogSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['tag_name']


class PostBlogViewSet(viewsets.ModelViewSet):
    """
    pagination --> 20item
    """
    serializer_class = PostBlogSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ('category', 'tags')
    search_fields = ('post_title', 'post_introduction', 'post_body')
    ordering_fields = ('created_at', 'read_count', 'likes')
    pagination_class = CommonPagination

    @action(detail=True, methods=['post'])
    def like(self, request, pk=None):
        post = self.get_object()
        post.likes += 1
        post.save()
        return Response({'status': 'liked', 'likes': post.likes})

    @action(detail=True, methods=['post'])
    def increment_read_count(self, request, pk=None):
        post = self.get_object()
        post.read_count += 1
        post.save()
        return Response({'status': 'read count incremented', 'read_count': post.read_count})

    def get_queryset(self):
        return PostBlog.objects.filter(
            is_publish=True, category_id=self.kwargs['category_pk']
        ).prefetch_related(
            "author",
            "tags"
        ).only(
            "author__first_name",
            "author__last_name",
            "tags__tag_name",
            "category__category_name",
            "created_at",
            "updated_at",
            "read_count",
            "post_introduction",
            "post_title",
            "post_slug",
            "post_body",
            "read_time",
            "post_cover_image",
            "likes",
            "is_publish",
            "description_slug"
        )

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            self.permission_classes =  (permissions.AllowAny,)
        else:
            self.permission_classes = (permissions.IsAdminUser,)
        return super().get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['category_pk'] = self.kwargs['category_pk']
        return context


class FavouritePostViewSet(viewsets.ModelViewSet):
    serializer_class = FavouritePostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FavouritePost.objects.filter(user=self.request.user).defer("is_deleted", "deleted_at")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentBlogViewSet(viewsets.ModelViewSet):
    """
    filter query --> ?is_pined=1 (1 equal comment is pined)
    """
    serializer_class = CommentBlogSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        return CommentBlog.objects.filter(
            is_publish=True, reply=None, post_id=self.kwargs['post_pk']
        ).defer("is_deleted", "deleted_at")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['post_pk'] = self.kwargs['post_pk']
        return context

    def filter_queryset(self, queryset):
        is_pined = self.request.query_params.get("is_pined", None)

        if is_pined and is_pined == 1:
            return queryset.filter(is_pined=True)
        return queryset
