from django.urls import path
from rest_framework import urls

from . import views


app_name = "v1_coupon"

urlpatterns = [
    path("validate_coupon_code/", views.ValidateCouponCodeView.as_view(), name="validate_coupon_code"),
]

