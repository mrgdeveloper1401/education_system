from rest_framework_nested import routers
from rest_framework.urls import path
from django.urls import include

from . import views

app_name = 'blogs'

router = routers.DefaultRouter()
router.register("category", views.BlogCategoryViewSet, basename="blog_category")

category_router = routers.NestedDefaultRouter(router, "category", lookup="category")
category_router.register("blog_posts", views.BlogPostViewSet, basename="blog_post")

course_router = routers.NestedDefaultRouter(category_router, "blog_posts", lookup="post")
course_router.register("comment", views.BlogCommentViewSet, basename="blog_comment")

urlpatterns = [
    path("", include(category_router.urls)),
    path("", include(course_router.urls)),

] + router.urls
