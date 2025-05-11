from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework import mixins


from advertise.models import ConsultationTopic, ConsultationSchedule, ConsultationSlot, ConsultationRequest
from utils.pagination import AnswerPagination, SlotPagination
# from utils.base_api import CrudApi
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
    queryset = ConsultationSlot.objects.select_related('schedule')
    serializer_class = ConsultationSlotSerializer
    # pagination_class = SlotPagination

    def get_permissions(self):
        if self.request.method in ['POST', "PUT", "PATCH", "DELETE"]:
            return [IsAdminUser()]
        return super().get_permissions()


class ConsultationRequestViewSet(ModelViewSet):
    queryset = ConsultationRequest.objects.select_related("slot")
    serializer_class = UserConsultationRequestSerializer

    def get_permissions(self):
        if self.request.method in ["PUT", "PATCH", "DELETE", "GET"]:
            return [IsAdminUser()]
        return super().get_permissions()
    
    # def get_serializer(self, *args, **kwargs):
    #     if self.request.method in ["PUT", "PATCH", "DELETE"]:
    #         return AdminConsultationRequestSerializer(*args, **kwargs)
    #     return super().get_serializer()


class AnswerViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin, GenericViewSet):
    serializer_class = ConsultationRequestAnswerSerializer
    queryset = ConsultationRequest.objects.select_related("slot")
    permission_classes = [IsAdminUser]
    pagination_class = AnswerPagination
