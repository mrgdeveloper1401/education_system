from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAdminUser

from advertise.models import UserAdvertise, IntervalAdvertise
from .pagination import AdvertisePagination
from .serializers import AdvertiseSerializer, DefineAdvertiseSerializer, AnsweredAdvertiseSerializer


class AdvertiseViewSet(CreateModelMixin, GenericViewSet):
    queryset = UserAdvertise.objects.all()
    serializer_class = AdvertiseSerializer


class DefineAdvertiseViewSet(ModelViewSet):
    queryset = IntervalAdvertise.objects.all()
    serializer_class = DefineAdvertiseSerializer
    permission_classes = [IsAdminUser]


class AnsweredAdvertiseViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = IntervalAdvertise.objects.all()
    serializer_class = AnsweredAdvertiseSerializer
    permission_classes = [IsAdminUser]
    pagination_class = AdvertisePagination


class WaitingAdvertiseViewSet(ModelViewSet):
    queryset = IntervalAdvertise.objects.all()
    serializer_class = AnsweredAdvertiseSerializer
    permission_classes = [IsAdminUser]
    pagination_class = AdvertisePagination
