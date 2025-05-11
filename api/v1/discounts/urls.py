from rest_framework import routers

from . import views

app_name = "v1_discounts"

router = routers.DefaultRouter()
router.register(r'discounts', views.DiscountViewSet)
router.register("first_one_coupon", views.FirstOneCouponViewSet, basename="first_one_coupon")

urlpatterns = []
urlpatterns += router.urls
