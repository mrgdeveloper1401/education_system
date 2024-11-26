from rest_framework.routers import DefaultRouter
from rest_framework.urls import path

from .views import ConsultationTopicViewSet, ConsultationScheduleViewSet, ConsultationSlotViewSet, \
    ConsultationRequestViewSet, AnswerApiView

app_name = 'advertise'
router = DefaultRouter()
router.register('topic', ConsultationTopicViewSet)
router.register('schedule', ConsultationScheduleViewSet)
router.register('slot', ConsultationSlotViewSet)
router.register('request', ConsultationRequestViewSet)
urlpatterns = [
    path('answered/', AnswerApiView.as_view(), name='answered'),
    path('answered/<int:pk>/', AnswerApiView.as_view(), name='detail-answered'),
]
urlpatterns += router.urls
