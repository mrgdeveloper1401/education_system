from rest_framework import routers

from api.v1.subscription.views import SubscriptionViewSet

app_name = "v1_subscription"

router = routers.DefaultRouter()

router.register(r"subscriptions", SubscriptionViewSet, basename="subscription")

urlpatterns = router.urls
