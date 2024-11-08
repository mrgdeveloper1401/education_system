from rest_framework.routers import DefaultRouter
from rest_framework.urls import path

from .views import UserViewSet, SendCodeOtpViewSet, VerifyOtpCodeApiView

router = DefaultRouter()
router.register('user', UserViewSet, basename='create')
router.register('send-code', SendCodeOtpViewSet, basename='login-otp')

app_name = 'users'
urlpatterns = [
    path("verify-otp/", VerifyOtpCodeApiView.as_view(), name="verify-otp"),
] + router.urls
