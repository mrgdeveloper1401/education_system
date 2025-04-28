from rest_framework import routers

from api.v1.orders.views import OrderViewSet


app_name = "v1_orders"

router = routers.DefaultRouter()

router.register("orders", OrderViewSet)

urlpatterns = []
urlpatterns += router.urls
