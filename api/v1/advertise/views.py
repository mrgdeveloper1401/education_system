from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework import mixins


from advertise.models import ConsultationTopic, ConsultationSchedule, ConsultationSlot, ConsultationRequest
from utils.pagination import AnswerPagination, SlotPagination
# from utils.base_api import CrudApi
from .serializers import ConsultationTopicSerializer, ConsultationScheduleSerializer, ConsultationSlotSerializer, \
    UserConsultationRequestSerializer, ConsultationRequestAnswerSerializer, AdminConsultationRequestSerializer


class ConsultationTopicViewSet(ModelViewSet):
    queryset = ConsultationTopic.objects.only("name",)
    serializer_class = ConsultationTopicSerializer

    def get_permissions(self):
        if self.request.method in ('POST', "PUT", "PATCH", "DELETE"):
            return (IsAdminUser(),)
        return super().get_permissions()


class ConsultationScheduleViewSet(ModelViewSet):
    queryset = ConsultationSchedule.objects.defer('deleted_at', "is_deleted")
    serializer_class = ConsultationScheduleSerializer
    permission_classes = (IsAdminUser,)


class ConsultationSlotViewSet(ModelViewSet):
    queryset = ConsultationSlot.objects.select_related('schedule',).defer('deleted_at', "is_deleted")
    serializer_class = ConsultationSlotSerializer

    def get_permissions(self):
        if self.request.method in ('POST', "PUT", "PATCH", "DELETE"):
            return (IsAdminUser(),)
        return super().get_permissions()


class ConsultationRequestViewSet(ModelViewSet):
    queryset = ConsultationRequest.objects.select_related("slot").only(
        "slot__is_available",
        "slot__date",
        "mobile_phone",
        "first_name",
        "last_name",
        "is_answer",
        "topic",
        "created_at",
        "updated_at"
    )
    serializer_class = UserConsultationRequestSerializer

    def get_permissions(self):
        if self.request.method in ("PUT", "PATCH", "DELETE", "GET"):
            return (IsAdminUser(),)
        return super().get_permissions()


class AnswerViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin,
                    mixins.DestroyModelMixin, GenericViewSet):
    serializer_class = ConsultationRequestAnswerSerializer
    queryset = ConsultationRequest.objects.select_related("slot").only(
        "slot__is_available",
        "slot__date",
        "mobile_phone",
        "first_name",
        "last_name",
        "is_answer",
        "topic",
        "created_at",
        "updated_at"
    )
    permission_classes = (IsAdminUser,)
    pagination_class = AnswerPagination
