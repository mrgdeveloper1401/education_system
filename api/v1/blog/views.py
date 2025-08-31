from django.db import IntegrityError
from drf_spectacular.utils import extend_schema
from rest_framework import viewsets, permissions, filters, generics, exceptions, status, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Prefetch, F
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from blog_app.models import CategoryBlog, PostBlog, TagBlog, FavouritePost, CommentBlog, Like
from utils.pagination import CommonPagination
from .serializers import (
    CategoryBlogSerializer,
    PostBlogSerializer,
    TagBlogSerializer,
    FavouritePostSerializer,
    CommentBlogSerializer,
    CreateCategorySerializer,
    AuthorListSerializer,
    LatestPostSerializer,
    LikePostBlogSerializer,
    IncrementPostBlogSerializer,
    ListPostBlogSerializer
)


class CategoryBlogViewSet(viewsets.ModelViewSet):
    """
    search --> ?name=category_name
    """
    queryset = CategoryBlog.objects.filter(is_publish=True).defer("is_deleted", "deleted_at")

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
            return CategoryBlogSerializer

    def destroy(self, request, *args, **kwargs):
        try:
            instance = self.get_object()
            instance.delete()
        except IntegrityError:
            raise exceptions.ValidationError(
                {"message": "این دسته بندی نمی‌تواند حذف شود زیرا چندین پست به آن وابسته است."}
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagBlogViewSet(viewsets.ModelViewSet):
    queryset = TagBlog.objects.filter(is_publish=True)
    serializer_class = TagBlogSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    filter_backends = [filters.SearchFilter]
    search_fields = ('tag_name',)


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
    lookup_field = 'post_slug'

    @extend_schema(request=None, responses=None)
    @action(detail=True, methods=['post'], serializer_class=LikePostBlogSerializer)
    def like(self, request, pk=None, category_pk=None):

        # validate user has like this post ??
        like = Like.objects.filter(
            user=request.user,
            post_id=pk
        )

        # check like
        if not like.exists():
            Like.objects.create(post_id=pk, user=request.user)
        else:
            raise exceptions.ValidationError({"message": _("you have already like this post")})

        # save like in post and get post
        PostBlog.objects.filter(is_publish=True, id=pk).only("post_title").update(likes=F("likes") + 1)
        return Response({'status': 'success'}, status=status.HTTP_201_CREATED)

    @extend_schema(responses=None, request=None)
    @action(detail=True, methods=['post'], serializer_class=IncrementPostBlogSerializer)
    def increment_read_count(self, request, pk=None, category_pk=None):
        # update query
        PostBlog.objects.filter(is_publish=True, id=pk).only("post_title").update(read_count=F("read_count") + 1)
        return Response({'status': 'read count incremented'}, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = PostBlog.objects.filter(
            is_publish=True, category_id=self.kwargs['category_pk']
        ).prefetch_related(
            Prefetch(
                "author", queryset=User.objects.only("first_name", "last_name")
            ),
            Prefetch(
                "tags", queryset=TagBlog.objects.only("tag_name")
            )
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
        if self.action == "list":
            queryset = queryset.defer("post_body", "read_count", "read_time", "likes")
        return queryset

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS or self.action == "increment_read_count":
            self.permission_classes =  (permissions.AllowAny,)
        elif self.action == "like":
            self.permission_classes = (IsAuthenticated,)
        else:
            self.permission_classes = (permissions.IsAdminUser,)
        return super().get_permissions()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['category_pk'] = self.kwargs['category_pk']
        return context

    def get_serializer_class(self):
        if self.action == "list":
            return ListPostBlogSerializer
        else:
            return super().get_serializer_class()


class FavouritePostViewSet(viewsets.ModelViewSet):
    serializer_class = FavouritePostSerializer
    permission_classes = (permissions.IsAuthenticated,)

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


class AuthorListView(generics.ListAPIView):
    """
    search --> ?search=mobile_phone
    permission --> admin user
    """
    queryset = User.objects.filter(
        is_active=True,
    ).only(
        "first_name",
        "last_name",
        "mobile_phone"
    )
    serializer_class = AuthorListSerializer
    # permission_classes = (permissions.IsAdminUser,)
    search_fields = ("mobile_phone",)
    filter_backends = (filters.SearchFilter,)


class LatestPostViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = LatestPostSerializer
    lookup_field = "post_slug"

    def get_queryset(self):
         return PostBlog.objects.filter(
            is_publish=True
        ).only(
            "category_id",
            "post_title",
            "post_introduction",
            "author",
            "post_cover_image",
            "post_slug",
            "created_at",
            "updated_at"
        ).prefetch_related(
            Prefetch(
                "author", queryset=User.objects.only("first_name", "last_name", 'mobile_phone'),
            )
        )

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()[:10]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class AllPostBlogViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    serializer_class = LatestPostSerializer
    lookup_field = "post_slug"
    pagination_class = CommonPagination

    def get_queryset(self):
         return PostBlog.objects.filter(
            is_publish=True
        ).only(
            "category_id",
            "post_title",
            "post_introduction",
            "author",
            "post_cover_image",
            "post_slug",
            "created_at",
            "updated_at"
        ).prefetch_related(
            Prefetch(
                "author", queryset=User.objects.only("first_name", "last_name", 'mobile_phone'),
            )
        )