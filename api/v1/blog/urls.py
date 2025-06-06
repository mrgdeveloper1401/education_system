from django.urls import path, include
from rest_framework_nested import routers

from .views import (
    CategoryBlogViewSet,
    PostBlogViewSet,
    TagBlogViewSet,
    FavouritePostViewSet,
    CommentBlogViewSet,
    AuthorListView,
    LatestPostView
)

router = routers.DefaultRouter()

app_name= "v1_blog"

router.register(r'categories', CategoryBlogViewSet, basename="blog_category")

category_router = routers.NestedDefaultRouter(router, "categories", lookup="category")
category_router.register(r'posts', PostBlogViewSet, basename="blog_post")

post_router = routers.NestedDefaultRouter(category_router, "posts", lookup="post")
post_router.register("comments", CommentBlogViewSet, basename="blog_comment")

router.register(r'tags', TagBlogViewSet, basename="blog_tag")
router.register(r'favourites', FavouritePostViewSet, basename="blog_favourite")

urlpatterns = [
    path('', include(router.urls)),
    path('', include(category_router.urls)),
    path('', include(post_router.urls)),
    path("author_list/", AuthorListView.as_view(), name="author_list"),
    path("latest_post/", LatestPostView.as_view(), name='latest_post')
]
