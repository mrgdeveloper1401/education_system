from django.db.models import Prefetch
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import get_object_or_404
from rest_framework.filters import SearchFilter
from rest_framework import exceptions
from rest_framework import viewsets

from accounts.models import User, State, City, Student, Coach, Ticket, TicketRoom, BestStudent, BestStudentAttribute
from utils.filters import UserFilter
from utils.pagination import StudentCoachTicketPagination, ListUserPagination
from utils.permissions import NotAuthenticate
from .pagination import UserPagination, CityPagination, BestStudentPagination
from .permissions import TicketRoomPermission
from .serializers import UserSerializer, OtpLoginSerializer, VerifyOtpSerializer, UpdateUserSerializer \
    , StateSerializer, CitySerializer, ChangePasswordSerializer, ForgetPasswordSerializer, \
    ConfirmForgetPasswordSerializer, StudentSerializer, CoachSerializer, CreateTicketSerializer, ListUserSerializer, \
    TickerRoomSerializer, ListTicketChatSerializer, UpdateTicketChatSerializer, ListBestStudentSerializer, \
    UserLoginSerializer


class UserLoginApiView(APIView):
    serializer_class = UserLoginSerializer
    permission_classes = [NotAuthenticate]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        valid_token = serializer.validated_data['token']
        response = Response(valid_token)
        response.set_cookie(
            key='token',
            value=valid_token,
            httponly=True,
            secure=True,
            samesite='Lax'
        )
        return response


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
    serializer_class = OtpLoginSerializer
    permission_classes = [NotAuthenticate]


class VerifyOtpCodeApiView(APIView):
    permission_classes = [NotAuthenticate]
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


class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    pagination_class = StudentCoachTicketPagination


class CoachViewSet(ModelViewSet):
    queryset = Coach.objects.all()
    serializer_class = CoachSerializer
    pagination_class = StudentCoachTicketPagination


class TicketRoomViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TickerRoomSerializer

    def get_queryset(self):
        return TicketRoom.objects.filter(user=self.request.user).only("id", "title_room")

    def get_serializer_context(self):
        return {"user": self.request.user}


class TicketChatViewSet(ModelViewSet):
    """
    send ticket user to admin
    """""
    pagination_class = StudentCoachTicketPagination
    permission_classes = [TicketRoomPermission]

    def get_serializer_class(self):
        if self.action == "list":
            return ListTicketChatSerializer
        if self.action in ['update', "partial_update", "destroy", "retrieve"]:
            return UpdateTicketChatSerializer
        if self.action == "create":
            return CreateTicketSerializer
        else:
            raise exceptions.NotAcceptable()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['room_pk'] = self.kwargs['ticket_room_pk']
        return context

    def get_queryset(self):
        if self.action == "list":
            return Ticket.objects.filter(room_id=self.kwargs['ticket_room_pk'], room__is_close=False).only("id")
        return Ticket.objects.filter(room_id=self.kwargs['ticket_room_pk'], room__is_close=False).only(
            "id", "ticket_body", "ticket_image", "sender__mobile_phone", "created_at"
        ).select_related("sender")


class ListUserApiView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = ListUserSerializer
    pagination_class = ListUserPagination
    permission_classes = [IsAdminUser]


class BestStudentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ListBestStudentSerializer
    pagination_class = BestStudentPagination

    def get_queryset(self):
        best_student_attributes_qs = BestStudentAttribute.objects.only("id", "best_student_id", "attribute")

        queryset = BestStudent.objects.select_related("student__user").filter(is_publish=True).only(
            "id", "student__user__first_name", "student__user__last_name", "description", "student__user__image"
        ).prefetch_related(
            Prefetch("attributes", queryset=best_student_attributes_qs)
        )
        return queryset
