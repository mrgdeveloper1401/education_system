from rest_framework.routers import DefaultRouter
from rest_framework.urls import path

from .views import UserViewSet, SendCodeOtpViewSet, VerifyOtpCodeApiView, StateApiView, CityApiView

router = DefaultRouter()
router.register('user', UserViewSet, basename='create')
router.register('send-code', SendCodeOtpViewSet, basename='login-otp')

app_name = 'users'
urlpatterns = [
    path("verify-otp/", VerifyOtpCodeApiView.as_view(), name="verify-otp"),
    path('state-list/', StateApiView.as_view(), name='state-list'),
    path('state-list/<int:pk>/', StateApiView.as_view(), name='detail-state-list'),
    path('city-list/', CityApiView.as_view(), name='city-list'),
    path('city-list/<int:pk>/', CityApiView.as_view(), name='city-detail'),
] + router.urls
