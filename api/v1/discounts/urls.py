from rest_framework import routers

from . import views

app_name = "v1_discounts"

router = routers.DefaultRouter()
router.register(r'discounts', views.DiscountViewSet)

urlpatterns = []
urlpatterns += router.urls
