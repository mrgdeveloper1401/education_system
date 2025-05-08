from rest_framework import viewsets, permissions, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from blog_app.models import CategoryBlog, PostBlog, TagBlog, FavouritePost, CommentBlog
from .serializers import (
    CategoryBlogSerializer,
    PostBlogSerializer,
    TagBlogSerializer,
    FavouritePostSerializer,
    CommentBlogSerializer
)


class CategoryBlogViewSet(viewsets.ModelViewSet):
    queryset = CategoryBlog.objects.filter(is_publish=True)
    serializer_class = CategoryBlogSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['category_name', 'category_slug']

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            self.permission_classes =  (permissions.AllowAny,)
        else:
            self.permission_classes = (permissions.IsAdminUser,)
        return super().get_permissions()


class TagBlogViewSet(viewsets.ModelViewSet):
    queryset = TagBlog.objects.filter(is_publish=True)
    serializer_class = TagBlogSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['tag_name']


class PostBlogViewSet(viewsets.ModelViewSet):
    queryset = PostBlog.objects.filter(is_publish=True)
    serializer_class = PostBlogSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'tags']
    search_fields = ['post_title', 'post_introduction', 'post_body']
    ordering_fields = ['created_at', 'read_count', 'likes']

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


class FavouritePostViewSet(viewsets.ModelViewSet):
    serializer_class = FavouritePostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FavouritePost.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CommentBlogViewSet(viewsets.ModelViewSet):
    serializer_class = CommentBlogSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        return CommentBlog.objects.filter(is_publish=True, reply=None)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
