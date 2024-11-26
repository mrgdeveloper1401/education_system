from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from advertise.models import ConsultationTopic, ConsultationSchedule, ConsultationSlot, ConsultationRequest
from .serializers import ConsultationTopicSerializer, ConsultationScheduleSerializer, ConsultationSlotSerializer, \
    ConsultationRequestSerializer


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

    def get_permissions(self):
        if self.request.method in ['POST', "PUT", "PATCH", "DELETE"]:
            return [IsAdminUser()]
        return super().get_permissions()


class ConsultationSlotViewSet(ModelViewSet):
    queryset = ConsultationSlot.objects.select_related('schedule').filter(is_available=True)
    serializer_class = ConsultationSlotSerializer
    
    def get_permissions(self):
        if self.request.method in ['POST', "PUT", "PATCH", "DELETE"]:
            return [IsAdminUser()]
        return super().get_permissions()


class ConsultationRequestViewSet(ModelViewSet):
    queryset = ConsultationRequest.objects.select_related('topic', "slot")
    serializer_class = ConsultationRequestSerializer
    
    def get_permissions(self):
        if self.request.method in ['POST', "PUT", "PATCH", "DELETE"]:
            return [IsAdminUser()]
        return super().get_permissions()
