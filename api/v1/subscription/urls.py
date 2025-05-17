from rest_framework import routers
from rest_framework.urls import path

from api.v1.subscription.views import SubscriptionViewSet, PaymentSubscriptionViewSet, PayApiView, VerifyPaymentView

app_name = "v1_subscription"

router = routers.DefaultRouter()

router.register(r"subscriptions", SubscriptionViewSet, basename="subscription")
router.register("payment_subscriptions", PaymentSubscriptionViewSet, basename="payment_subscription")

urlpatterns = [
    path("payment_link/", PayApiView.as_view(), name='pay'),
    path("verify_payment/", VerifyPaymentView.as_view(), name='verify_payment'),
] + router.urls
