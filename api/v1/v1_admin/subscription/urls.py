from rest_framework.routers import DefaultRouter
from .views import SubscriptionViewSet, PlanViewSet

app_name = "api_subscription_admin"

router = DefaultRouter()
# router.register(r'subscriptions', SubscriptionViewSet, basename='subscription')
# router.register(r'plans', PlanViewSet, basename='plan')

urlpatterns = router.urls
