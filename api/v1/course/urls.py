from rest_framework_nested import routers
from django.urls import include
from rest_framework.urls import path

from . import views

router = routers.DefaultRouter()
router.register('term', views.CategoryViewSet, basename='category')
# router.register('course', views.CourseViewSet, basename='course')

term_router = routers.NestedSimpleRouter(router, r'term', lookup='category')
term_router.register('course', views.CourseViewSet, basename='nested-course')


app_name = 'course'
urlpatterns = [
    path('', include(term_router.urls)),
]
urlpatterns += router.urls
