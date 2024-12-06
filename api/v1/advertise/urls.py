from rest_framework.routers import DefaultRouter

from .views import ConsultationTopicViewSet, ConsultationScheduleViewSet, ConsultationSlotViewSet, \
    ConsultationRequestViewSet, AnswerViewSet

app_name = 'advertise'
router = DefaultRouter()
router.register('topic', ConsultationTopicViewSet)
router.register('schedule', ConsultationScheduleViewSet)
router.register('slot', ConsultationSlotViewSet)
router.register('request', ConsultationRequestViewSet)
router.register('answered', AnswerViewSet, basename='ConsultationAnswer')

urlpatterns = router.urls
