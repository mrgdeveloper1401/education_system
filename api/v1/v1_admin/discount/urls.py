from rest_framework import routers

from . import views

app_name = "admin_discount"

router = routers.SimpleRouter()

router.register("coupon", views.CouponViewSet, basename="coupon")

urlpatterns = router.urls
