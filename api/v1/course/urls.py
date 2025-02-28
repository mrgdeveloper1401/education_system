from rest_framework_nested import routers
from django.urls import include
from rest_framework.urls import path

from . import views

router = routers.DefaultRouter()
router.register('category', views.CategoryViewSet, basename='term')

category_router = routers.NestedDefaultRouter(router, r'category', lookup='category')
category_router.register('course', views.CourseViewSet, basename='nested-course')

course_router = routers.NestedDefaultRouter(category_router, r'course', lookup='course')
course_router.register('section', views.SectionViewSet, basename='nested-section')
course_router.register('comment', views.CommentViewSet, basename='nested-comment')

section_router = routers.NestedDefaultRouter(course_router, "section", lookup="section")
section_router.register("section_video", views.SectionVideoViewSet, basename="section_video")
section_router.register("section_file", views.SectionFileViewSet, basename="section_file")

section_file_router = routers.NestedDefaultRouter(section_router, r'section_file', lookup="section_file")
section_file_router.register("send_section_file", views.SendSectionFileViewSet, basename="send_section_file")

app_name = 'course'
urlpatterns = [
    path('', include(category_router.urls)),
    path('', include(course_router.urls)),
    path("", include(section_router.urls)),
    path("", include(section_file_router.urls)),
]
urlpatterns += router.urls
