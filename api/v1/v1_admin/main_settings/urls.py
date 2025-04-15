from rest_framework import routers

from . import views

app_name = "admin_settings"

router = routers.SimpleRouter()

router.register(r'banners', views.BannerViewSet, basename='banner')

urlpatterns = router.urls
