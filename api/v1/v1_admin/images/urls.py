from rest_framework import routers

from . import views

app_name = "admin_image"

router = routers.DefaultRouter()
router.register(r'images', views.ImageViewSet, basename="admin_image")

urlpatterns = router.urls
