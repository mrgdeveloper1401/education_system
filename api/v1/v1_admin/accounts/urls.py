from rest_framework_nested import routers
from django.urls import include
from rest_framework.urls import path

from . import views


app_name = 'admin_account'

router = routers.DefaultRouter()

router.register("best_student", views.AdminBestStudentViewSet, basename="best_student")

urlpatterns = [
    path("student_list/", views.AdminStudentApiView.as_view(), name="student_list_"),
] + router.urls
