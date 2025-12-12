from rest_framework.routers import DefaultRouter

from .views import ConsultationTopicViewSet, ConsultationScheduleViewSet, ConsultationSlotViewSet, \
    ConsultationRequestViewSet, AnswerViewSet

app_name = 'advertise'
router = DefaultRouter()

router.register('topic', ConsultationTopicViewSet, basename='topic')
router.register('schedule', ConsultationScheduleViewSet, basename='schedule')
router.register('slot', ConsultationSlotViewSet, basename='slot')
router.register('request', ConsultationRequestViewSet, basename='request')
router.register('answered', AnswerViewSet, basename='ConsultationAnswer')

urlpatterns =  router.urls
