from rest_framework_nested import routers
from django.urls import include
from rest_framework.urls import path

from . import views

router = routers.DefaultRouter()
router.register('term', views.TermViewSet, basename='term')

term_router = routers.NestedSimpleRouter(router, r'term', lookup='term')
term_router.register('course', views.CourseViewSet, basename='course')


app_name = 'course'
urlpatterns = [
    path('', include(term_router.urls)),
]
urlpatterns += router.urls
