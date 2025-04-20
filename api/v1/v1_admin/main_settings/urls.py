from rest_framework import routers

from . import views

app_name = "admin_settings"

router = routers.SimpleRouter()

router.register(r'banners', views.BannerViewSet, basename='banner')
router.register("header_sites", views.HeaderSiteViewSet, basename='header_site')

urlpatterns = router.urls
