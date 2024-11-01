from rest_framework.routers import DefaultRouter
from rest_framework.urls import path

from .views import CreateUserViewSet, OtpVerifyApiView, ResendOtpCodeApiView

router = DefaultRouter()
router.register(r'create', CreateUserViewSet, basename='user')

app_name = 'users'
urlpatterns = [
    path('verify/', OtpVerifyApiView.as_view(), name='otp-verify'),
    path('resend/', ResendOtpCodeApiView.as_view(), name='resend-otp'),
] + router.urls
