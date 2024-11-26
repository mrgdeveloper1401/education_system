from rest_framework.routers import DefaultRouter

from .views import ConsultationTopicViewSet, ConsultationScheduleViewSet, ConsultationSlotViewSet, \
    ConsultationRequestViewSet

app_name = 'advertise'
router = DefaultRouter()
router.register('topic', ConsultationTopicViewSet)
router.register('schedule', ConsultationScheduleViewSet)
router.register('slot', ConsultationSlotViewSet)
router.register('request', ConsultationRequestViewSet)
urlpatterns = []
urlpatterns += router.urls
