from rest_framework_nested import routers
from rest_framework.urls import path
from django.urls import include

from . import views

router = routers.DefaultRouter()
router.register('user', views.UserViewSet, basename='create')
router.register("best_student", views.BestStudentViewSet, basename="best_student")
router.register("user_notification", views.UserNotificationViewSet, basename="user_notification")

router.register("ticket_room", views.TicketRoomViewSet, basename='ticket_room')

ticket_room_router = routers.NestedDefaultRouter(router, "ticket_room", lookup='ticket_room')
ticket_room_router.register("ticket_chat", views.TicketChatViewSet, basename='ticket_chat')

ticket_chat_router = routers.NestedDefaultRouter(ticket_room_router, "ticket_chat", lookup='ticket_chat')

app_name = 'users'

urlpatterns = [
    path('', include(ticket_room_router.urls)),
    path("", include(ticket_chat_router.urls)),
    path("otp_phone/", views.RequestPhoneView.as_view(), name='otp_phone'),
    path("otp_phone_verify/", views.RequestOtpVerifyView.as_view(), name='otp_phone_verify'),
    path("login/", views.UserLoginApiView.as_view(), name='user_login'),
    path("validate_token/", views.ValidateTokenApiView.as_view(), name='validate_token'),
    path('state-list/', views.StateApiView.as_view(), name='state-list'),
    path('state-list/<int:pk>/', views.StateApiView.as_view(), name='detail-state-list'),
    path('state/<int:pk>/city/', views.StateCitiesGenericView.as_view(), name='detail-state-city'),
    path('city-list/', views.CityApiView.as_view(), name='city-list'),
    path('city-list/<int:pk>/', views.CityApiView.as_view(), name='city-detail'),
    path('user/change-password/', views.ChangePasswordApiView.as_view(), name='change-password'),
    path('user/forget-password/', views.ForgetPasswordApiView.as_view(), name='forget-password'),
    path('user/confirm-forget-password/', views.ConfirmForgetPasswordApiView.as_view(), name='confirm-password'),
    path("invitation_list/", views.InvitationView.as_view(), name='invitation_list')
] + router.urls
