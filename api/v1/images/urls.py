from rest_framework import routers

from . import views

app_name = "v1_images"

router = routers.DefaultRouter()
router.register(r"images", views.ImageViewSet, basename="images")
urlpatterns = [] + router.urls
