from rest_framework_nested import routers
from django.urls import include
from rest_framework.urls import path

from . import views


app_name = 'admin_account'

router = routers.DefaultRouter()

router.register("best_student", views.AdminBestStudentViewSet, basename="best_student")

best_student_router = routers.NestedDefaultRouter(router, "best_student", lookup="best_student")
best_student_router.register("attribute", views.AdminBestStudentAttributeViewSet, basename="attribute")

urlpatterns = [
    path("", include(best_student_router.urls))
] + router.urls
