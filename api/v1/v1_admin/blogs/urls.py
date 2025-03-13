from rest_framework_nested import routers
from rest_framework.urls import path
from django.urls import include

from . import views

app_name = "admin_blog"
router = routers.DefaultRouter()

router.register("admin_blog_category", views.AdminCategoryBlogViewSet, basename="admin_blog_category")

category_blog_router = routers.NestedDefaultRouter(router, "admin_blog_category", lookup="category")
category_blog_router.register("admin_blog_post", views.AdminBlogPostViewSet, basename="admin_blog_post")

post_blog_router = routers.NestedDefaultRouter(category_blog_router, "admin_blog_post", lookup="post")
post_blog_router.register("admin_comment_blog", views.AdminCommentViewSet, basename="admin_comment_blog")

router.register("admin_tag_blog", views.AdminTagViewSet, basename="admin_tag_blog")
router.register("admin_favorite_post_blog", views.AdminFavoriteViewSet, basename="admin_favorite_post_blog")

urlpatterns = [
    path("", include(category_blog_router.urls)),
    path("", include(post_blog_router.urls)),
] + router.urls
