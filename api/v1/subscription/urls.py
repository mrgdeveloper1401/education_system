from rest_framework.urls import path
from rest_framework import routers

from . import views

app_name = "subscription"

router = routers.DefaultRouter()
router.register(r'subscriptions', views.SubscriptionViewSet, basename='subscriptions')
router.register(r'plan', views.PlanViewSet, basename='plan')
urlpatterns = router.urls
