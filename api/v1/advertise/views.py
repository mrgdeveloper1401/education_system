from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from advertise.models import ConsultationTopic, ConsultationSchedule, ConsultationSlot, ConsultationRequest
from utils.base_api import CrudApi
from .serializers import ConsultationTopicSerializer, ConsultationScheduleSerializer, ConsultationSlotSerializer, \
    UserConsultationRequestSerializer, ConsultationRequestAnswerSerializer, AdminConsultationRequestSerializer


class ConsultationTopicViewSet(ModelViewSet):
    queryset = ConsultationTopic.objects.all()
    serializer_class = ConsultationTopicSerializer

    def get_permissions(self):
        if self.request.method in ['POST', "PUT", "PATCH", "DELETE"]:
            return [IsAdminUser()]
        return super().get_permissions()


class ConsultationScheduleViewSet(ModelViewSet):
    queryset = ConsultationSchedule.objects.all()
    serializer_class = ConsultationScheduleSerializer
    permission_classes = [IsAdminUser]


class ConsultationSlotViewSet(ModelViewSet):
    queryset = ConsultationSlot.objects.select_related('schedule').filter(is_available=True)
    serializer_class = ConsultationSlotSerializer
    permission_classes = [IsAdminUser]


class ConsultationRequestViewSet(ModelViewSet):
    queryset = ConsultationRequest.objects.select_related('topic', "slot")
    serializer_class = UserConsultationRequestSerializer
    
    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAdminUser()]
        return super().get_permissions()


class AnswerApiView(CrudApi):
    serializer_class = ConsultationRequestAnswerSerializer
    queryset = ConsultationSlot.objects.all()
    permission_classes = [IsAdminUser]
