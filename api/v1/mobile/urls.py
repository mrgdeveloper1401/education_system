from rest_framework.urls import path
from rest_framework.routers import SimpleRouter
from . import views


app_name = "v1_mobile"
router = SimpleRouter()
router.register("list_detail_course", views.ListDetailCourseView, basename="list_detail_course")

urlpatterns = [
    path("list_category/", views.ListCategoryView.as_view(), name="list_category"),
] + router.urls
