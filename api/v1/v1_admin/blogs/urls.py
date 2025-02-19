from rest_framework import routers

from . import views

app_name = "admin_blog"
router = routers.DefaultRouter()

router.register("admin_blog_category", views.AdminCategoryBlogViewSet, basename="admin_blog_category")
router.register("admin_blog_post", views.AdminBlogPostViewSet, basename="admin_blog_post")
router.register("admin_tag_blog", views.AdminTagViewSet, basename="admin_tag_blog")
router.register("admin_favorite_blog", views.AdminFavoriteViewSet, basename="admin_favorite_blog")
router.register("admin_comment_blog", views.AdminCommentViewSet, basename="admin_comment_blog")

urlpatterns = []
urlpatterns += router.urls
