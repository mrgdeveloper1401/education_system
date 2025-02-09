from rest_framework import routers

from . import views

app_name = 'admin_category'

router = routers.DefaultRouter()

router.register('category', views.CategoryViewSet, basename='category')

urlpatterns = []
urlpatterns += router.urls
