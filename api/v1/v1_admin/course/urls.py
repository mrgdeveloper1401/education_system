from rest_framework_nested import routers
from django.urls import include
from rest_framework.urls import path

from . import views

app_name = 'admin_category'

router = routers.DefaultRouter()

router.register('category', views.CategoryViewSet, basename='category')

category_router = routers.NestedSimpleRouter(router, r'category', lookup='category')
category_router.register("course", views.AdminCourseViewSet, basename='course')

course_router = routers.NestedDefaultRouter(category_router, r'course', lookup='course')
course_router.register("course_section", views.AdminCourseSectionViewSet, basename='course_section')

urlpatterns = [
    path("", include(category_router.urls)),
    path('', include(course_router.urls))
]
urlpatterns += router.urls
