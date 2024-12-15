from rest_framework import routers

from . import views

app_name = 'coupons'

router = routers.DefaultRouter()
router.register(r'coupons', views.CouponViewSet, basename='coupons')
router.register(r'discount', views.DiscountViewSet, basename='discount')

urlpatterns = router.urls
