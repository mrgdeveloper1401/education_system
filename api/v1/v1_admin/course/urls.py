from rest_framework_nested import routers
from django.urls import include
from rest_framework.urls import path

from . import views

app_name = 'admin_category'

router = routers.DefaultRouter()

router.register('category', views.CategoryViewSet, basename='category')
router.register("certificate", views.AdminCertificateViewSet, basename='admin_certificate')

category_router = routers.NestedSimpleRouter(router, r'category', lookup='category')
category_router.register("course", views.AdminCourseViewSet, basename='course')

course_router = routers.NestedDefaultRouter(category_router, r'course', lookup='course')
course_router.register("course_section", views.AdminCourseSectionViewSet, basename='course_section')
course_router.register("class_room", views.AdminLessonCourseViewSet, basename='class_room')

section_router = routers.NestedDefaultRouter(course_router, r'course_section', lookup='section')
section_router.register('section_file', views.AdminSectionFileViewSet, basename='section_file')
section_router.register("section_video", views.AdminSectionVideoViewSet, basename='section_video')

section_file_router = routers.NestedDefaultRouter(section_router, r'section_file', lookup='section_file')
section_file_router.register("section_score", views.AdminSectionScoreViewSet, basename='section_score')

urlpatterns = [
    path("", include(category_router.urls)),
    path('', include(course_router.urls)),
    path("", include(section_router.urls)),
    path("", include(section_file_router.urls)),
    path('course_list/', views.AdminCourseListApiView.as_view(), name='course_list')
]
urlpatterns += router.urls
