from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAdminUser

from advertise.models import Advertise, DefineAdvertise
from .pagination import AdvertisePagination
from .serializers import AdvertiseSerializer, DefineAdvertiseSerializer, AnsweredAdvertiseSerializer


class AdvertiseViewSet(CreateModelMixin, GenericViewSet):
    queryset = Advertise.objects.filter(slot__is_available=True)
    serializer_class = AdvertiseSerializer


class DefineAdvertiseViewSet(ModelViewSet):
    queryset = DefineAdvertise.objects.all()
    serializer_class = DefineAdvertiseSerializer
    permission_classes = [IsAdminUser]


class AnsweredAdvertiseViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = Advertise.objects.filter(answered=True).select_related('slot')
    serializer_class = AnsweredAdvertiseSerializer
    permission_classes = [IsAdminUser]
    pagination_class = AdvertisePagination
