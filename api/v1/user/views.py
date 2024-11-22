from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.generics import get_object_or_404
from rest_framework.filters import SearchFilter

from accounts.models import User, Otp, State, City
from utils.filters import UserFilter
from utils.permissions import NotAuthenticate
from .pagination import UserPagination, CityPagination
from .serializers import UserSerializer, OtpLoginSerializer, VerifyOtpSerializer, UpdateUserSerializer \
    , StateSerializer, CitySerializer, ChangePasswordSerializer, ForgetPasswordSerializer, \
    ConfirmForgetPasswordSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.select_related("state", "city")
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    pagination_class = UserPagination
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['is_staff', "gender"]
    filterset_class = UserFilter

    def get_serializer_class(self):
        if self.request.method in ['PUT', "PATCH"]:
            return UpdateUserSerializer
        return super().get_serializer_class()

    def perform_destroy(self, instance):
        instance.deactivate_user()


class SendCodeOtpViewSet(CreateModelMixin, GenericViewSet):
    queryset = Otp.objects.all()
    serializer_class = OtpLoginSerializer


class VerifyOtpCodeApiView(APIView):
    serializer_class = VerifyOtpSerializer

    def post(self, request, *args, **kwargs):
        ser_data = self.serializer_class(data=request.data)
        ser_data.is_valid(raise_exception=True)
        validated_data = ser_data.validated_data
        return Response({
            'refresh_token': validated_data['refresh'],
            'access_token': validated_data['access']
        }, status=HTTP_200_OK)


class BaseApiView(APIView):
    model = None
    serializer_class = None
    pagination_class = CityPagination

    def get_object(self, pk):
        return get_object_or_404(self.model, pk=pk)

    def get(self, request, *args, **kwargs):
        if 'pk' in self.kwargs:
            instance = self.get_object(pk=self.kwargs['pk'])
            serializer = self.serializer_class(instance)
            return Response(serializer.data, status=HTTP_200_OK)
        queryset = self.model
        paginator = self.pagination_class()
        paginator_queryset = paginator.paginate_queryset(queryset, request)
        serializer = self.serializer_class(paginator_queryset, many=True)
        return paginator.get_paginated_response(serializer.data)


class StateApiView(BaseApiView):
    model = State.objects.all()
    serializer_class = StateSerializer


class CityApiView(BaseApiView):
    model = City.objects.select_related("state")
    serializer_class = CitySerializer


class StateCitiesGenericView(ListAPIView):
    serializer_class = CitySerializer

    def get_queryset(self):
        return City.objects.filter(state_id=self.kwargs['pk']).select_related('state').order_by("city")


class ChangePasswordApiView(APIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'user': request.user})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_200_OK)


class ForgetPasswordApiView(APIView):
    serializer_class = ForgetPasswordSerializer
    permission_classes = [NotAuthenticate]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_200_OK)


class ConfirmForgetPasswordApiView(APIView):
    serializer_class = ConfirmForgetPasswordSerializer
    permission_classes = [NotAuthenticate]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTP_200_OK)
