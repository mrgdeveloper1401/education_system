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

section_router = routers.NestedDefaultRouter(course_router, r'course_section', lookup='section')
section_router.register("section_image", views.AdminSectionImagesViewSet, basename='section_image')
section_router.register('section_file', views.AdminSectionFileViewSet, basename='section_file')
section_router.register("section_video", views.AdminSectionVideoViewSet, basename='section_video')

urlpatterns = [
    path("", include(category_router.urls)),
    path('', include(course_router.urls)),
    path("", include(section_router.urls)),
]
urlpatterns += router.urls
