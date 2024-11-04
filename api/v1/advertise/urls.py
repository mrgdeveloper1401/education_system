from rest_framework.routers import DefaultRouter

from .views import AdvertiseViewSet, DefineAdvertiseViewSet, AnsweredAdvertiseViewSet, WaitingAdvertiseViewSet

app_name = 'advertise'
router = DefaultRouter()
router.register('reserve', AdvertiseViewSet, basename='advertise')
router.register('define', DefineAdvertiseViewSet, basename='define')
router.register('answered', AnsweredAdvertiseViewSet, basename="answered")
router.register('waiting', WaitingAdvertiseViewSet, basename="waiting")


urlpatterns = router.urls
