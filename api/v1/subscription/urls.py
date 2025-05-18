from rest_framework import routers
from rest_framework.urls import path

from . import views


app_name = "v1_subscription"

router = routers.DefaultRouter()

router.register(r"subscriptions", views.SubscriptionViewSet, basename="subscription")
router.register("payment_subscriptions", views.PaymentSubscriptionViewSet, basename="payment_subscription")
router.register("user_verify_payment", views.PaymentVerifyView, basename="user_verify_payment")

urlpatterns = [
    path("payment_link/", views.PayApiView.as_view(), name='pay'),
    path("verify_payment/", views.VerifyPaymentView.as_view(), name='verify_payment'),
] + router.urls
