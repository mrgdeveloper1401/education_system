from rest_framework.routers import DefaultRouter
from rest_framework.urls import path

from .views import UserViewSet, SendCodeOtpViewSet, VerifyOtpCodeApiView, StateApiView, CityApiView, \
    StateCitiesGenericView, ChangePasswordApiView, ForgetPasswordApiView, ConfirmForgetPasswordApiView, \
    StudentViewSet, CoachViewSet, TicketViewSet

router = DefaultRouter()
router.register('user', UserViewSet, basename='create')
router.register('send-code', SendCodeOtpViewSet, basename='login-otp')
router.register('student', StudentViewSet, basename='student')
router.register('coach', CoachViewSet, basename='coach')
router.register('ticket', TicketViewSet, basename='ticket')

app_name = 'users'
urlpatterns = [
    path("verify-otp/", VerifyOtpCodeApiView.as_view(), name="verify-otp"),
    path('state-list/', StateApiView.as_view(), name='state-list'),
    path('state-list/<int:pk>/', StateApiView.as_view(), name='detail-state-list'),
    path('state/<int:pk>/city/', StateCitiesGenericView.as_view(), name='detail-state-city'),
    path('city-list/', CityApiView.as_view(), name='city-list'),
    path('city-list/<int:pk>/', CityApiView.as_view(), name='city-detail'),
    path('user/change-password/', ChangePasswordApiView.as_view(), name='change-password'),
    path('user/forget-password/', ForgetPasswordApiView.as_view(), name='forget-password'),
    path('user/confirm-forget-password/', ConfirmForgetPasswordApiView.as_view(), name='confirm-password'),
] + router.urls
