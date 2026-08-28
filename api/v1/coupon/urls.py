from django.urls import path

from . import views


app_name = "v1_coupon"

urlpatterns = [
    path("validate_coupon_code/", views.ValidateCouponCodeView.as_view(), name="validate_coupon_code"),
]

