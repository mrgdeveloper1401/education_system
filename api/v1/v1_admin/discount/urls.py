from rest_framework import routers
from django.urls import path

from . import views

app_name = "admin_discount"

router = routers.SimpleRouter()

router.register("coupon", views.CouponViewSet, basename="coupon")
router.register("discount", views.DiscountViewSet, basename="discount")

urlpatterns = [
    path("discount_course/", views.DiscountCourseApiView.as_view(), name="discount_course"),
] + router.urls
