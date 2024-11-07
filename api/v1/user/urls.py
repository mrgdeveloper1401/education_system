from rest_framework.routers import DefaultRouter
from rest_framework.urls import path

from .views import UserViewSet

router = DefaultRouter()
router.register('user', UserViewSet, basename='create')

app_name = 'users'
urlpatterns = [

] + router.urls
