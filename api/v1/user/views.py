import jwt
from asgiref.sync import sync_to_async
from django.contrib.auth.hashers import make_password
from django.db.models import Prefetch
from django.utils import timezone
from django.utils.crypto import get_random_string
from django_filters.rest_framework.backends import DjangoFilterBackend
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS, IsAdminUser
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.generics import get_object_or_404
from rest_framework.filters import SearchFilter
from rest_framework import viewsets, status, generics
from django.middleware import csrf
from django.conf import settings
from rest_framework.validators import ValidationError
from drf_spectacular.utils import extend_schema, OpenApiParameter
from adrf.views import APIView as AsyncAPIView

from accounts.models import User, State, City, Student, Coach, Ticket, TicketRoom, BestStudent, PrivateNotification, \
    Otp, Invitation
from utils.filters import UserFilter
from utils.pagination import StudentCoachTicketPagination
from utils.permissions import NotAuthenticate
from .filters import TicketRoomFilter
from .pagination import UserPagination, CityPagination, BestStudentPagination
from .permissions import TicketRoomPermission
from education_system.base import SIMPLE_JWT
from . import serializers
from .utils import get_token_for_user
from ..course.paginations import CommonPagination
from ...utils.custom_permissions import AsyncNotAuthenticated
from ...utils.send_otp_sms import async_send_otp_sms


class UserLoginApiView(APIView):
    serializer_class = serializers.UserLoginSerializer
    permission_classes = (NotAuthenticate,)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get data
        validated_data = serializer.validated_data

        # authenticate user
        user = validated_data.get("user")
        response = Response()
        if user:
            if user.is_active:
                data = get_token_for_user(user)
                response.set_cookie(
                    key=SIMPLE_JWT['AUTH_COOKIE'],
                    value=data['access'],
                    expires=SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'],
                    secure=SIMPLE_JWT['AUTH_COOKIE_SECURE'],
                    httponly=SIMPLE_JWT['AUTH_COOKIE_HTTP_ONLY'],
                    samesite=SIMPLE_JWT['AUTH_COOKIE_SAMESITE'],
                )
                csrf.get_token(request)
                response.data = {
                    "data": data,
                    "is_staff": user.is_staff,
                    "is_coach": user.is_coach,
                    "full_name": user.get_full_name
                }
            else:
                return Response({"message": "this account is not active!"}, status=status.HTTP_403_FORBIDDEN)
        else:
            return Response({"message": "invalid username or password"}, status=status.HTTP_404_NOT_FOUND)
        return response


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.UserSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = UserPagination
    filter_backends = (DjangoFilterBackend, SearchFilter)
    filterset_fields = ('is_staff', "gender", "is_active")
    filterset_class = UserFilter

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = (IsAdminUser,)
        return super().get_permissions()

    def get_queryset(self):
        query = User.objects.select_related("state", "city").prefetch_related(
            Prefetch(
                "student", queryset=Student.objects.only("referral_code", "user_id")
            )
        )
        if self.request.user.is_staff:
            return query
        else:
            return query.filter(id=self.request.user.id)

    def get_serializer_class(self):
        if self.request.method in ('PUT', "PATCH"):
            return serializers.UpdateUserSerializer
        return super().get_serializer_class()


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


class StateApiView(APIView):
    serializer_class = serializers.StateSerializer
    queryset = State.objects.all

    def get(self, request, *args, **kwargs):
        serializer = self.serializer_class(self.queryset(), many=True)
        return Response(serializer.data, status=HTTP_200_OK)


class CityApiView(BaseApiView):
    model = City.objects.select_related("state").only("state", "city")
    serializer_class = serializers.CitySerializer


class StateCitiesGenericView(ListAPIView):
    serializer_class = serializers.CitySerializer

    def get_queryset(self):
        return City.objects.filter(state_id=self.kwargs['pk']).select_related('state').order_by("city")


class ChangePasswordApiView(APIView):
    serializer_class = serializers.ChangePasswordSerializer
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data

        new_password = validated_data.get('new_password')
        old_password = validated_data.get('old_password')
        confirm_password = validated_data.get('confirm_password')

        if new_password != confirm_password:
            raise ValidationError({"message": "پسورد ها با هم برابر نیستند"})
        if not request.user.check_password(old_password):
            raise ValidationError({"message": "پسورد فعلی شما صحیح نیست"})

        request.user.set_password(new_password)
        request.user.save()

        return Response(serializer.data, status=HTTP_200_OK)


class ForgetPasswordApiView(AsyncAPIView):
    serializer_class = serializers.ForgetPasswordSerializer
    permission_classes = (AsyncNotAuthenticated,)

    async def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get mobile phone in data
        mobile_phone = serializer.validated_data['mobile_phone']

        # check user exists
        if not await User.objects.filter(mobile_phone=mobile_phone, is_active=True).aexists():
            raise ValidationError({"message": "phone number dose not exits"})
        else:
            have_otp = await Otp.objects.filter(
                mobile_phone=mobile_phone,
                expired_date__gt=timezone.now()
            ).only(
                "mobile_phone", "expired_date"
            ).aexists()

            if have_otp:
                raise ValidationError({"message": "you have already otp code, please 2 minute wait"})
            else:
                otp = await Otp.objects.acreate(mobile_phone=mobile_phone)
                await async_send_otp_sms(otp.mobile_phone, otp.code)
                return Response({'message': "code sent"}, status=HTTP_200_OK)


class ConfirmForgetPasswordApiView(APIView):
    serializer_class = serializers.ConfirmForgetPasswordSerializer
    permission_classes = [NotAuthenticate]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code']
        password = serializer.validated_data['confirm_password']
        otp = Otp.objects.filter(code=code, expired_date__gt=timezone.now()).only("code").last()

        if not otp:
            raise ValidationError({"message": "otp is invalid or expired"})
        else:
            user = User.objects.filter(mobile_phone=otp.mobile_phone).only("mobile_phone", "password").last()

            if not user:
                raise ValidationError({"message": "user dose not exits"})
            else:
                user.set_password(password)
                otp.delete()
                return Response({"message": "password successfully change"}, status=HTTP_200_OK)


class StudentViewSet(ModelViewSet):
    queryset = Student.objects.all()
    serializer_class = serializers.StudentSerializer
    pagination_class = StudentCoachTicketPagination


class CoachViewSet(ModelViewSet):
    queryset = Coach.objects.all()
    serializer_class = serializers.CoachSerializer
    pagination_class = StudentCoachTicketPagination


class TicketRoomViewSet(ModelViewSet):
    """
    filter query --> ?is_close=false or is_close=true
    """
    permission_classes = (IsAuthenticated,)
    pagination_class = CommonPagination
    serializer_class = serializers.TickerRoomSerializer
    filterset_class = TicketRoomFilter
    filter_backends = (DjangoFilterBackend,)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="close", description="return all ticket room is close yes or no"
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        room = TicketRoom.objects.filter(is_active=True).only(
            "id", "title_room", "is_close", "created_at", "subject_room"
        )

        if self.request.user.is_staff is False:
            room = room.filter(user=self.request.user)

        # room_close = self.request.query_params.get("close")
        #
        # if room_close:
        #     room = room.filter(is_close=room_close)

        return room


class TicketChatViewSet(ModelViewSet):
    """
    send ticket user to admin
    """""
    permission_classes = (TicketRoomPermission,)
    serializer_class = serializers.TicketSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['room_pk'] = self.kwargs['ticket_room_pk']
        return context

    def get_queryset(self):
        ticket = Ticket.objects.filter(
            room_id=self.kwargs['ticket_room_pk'], is_publish=True, room__is_active=True).only(
            "ticket_body", "ticket_file", "created_at", "sender__first_name", "sender__last_name", "depth", "path",
            "numchild", "reply__first_name", "reply__last_name", "reply__mobile_phone"
        ).select_related("sender", "reply")

        user = self.request.user

        if hasattr(user, "student"):
            ticket = ticket.filter(sender=user)

        if hasattr(user, "coach") and not user.is_staff:
            ticket = ticket.filter(sender=user)

        if hasattr(user, "coach") and user.is_staff:
            ticket = ticket

        return ticket


class BestStudentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ListBestStudentSerializer
    pagination_class = BestStudentPagination

    def get_queryset(self):
        return BestStudent.objects.filter(is_publish=True).only(
            "student",
            "description",
            "student_image",
            "attributes"
        )


class ValidateTokenApiView(APIView):
    serializer_class = serializers.ValidateTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        response = Response()
        try:
            token = serializer.validated_data['token']
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=settings.SIMPLE_JWT['ALGORITHM'])
        except jwt.ExpiredSignatureError:
            raise ValidationError("Token has expired")
        except jwt.InvalidTokenError:
            raise ValidationError("Invalid token")
        else:
            response.data = 'valid token'
            response.status_code = HTTP_200_OK
            return response


class UserNotificationViewSet(viewsets.ModelViewSet):
    """
    for filter notification \n
    you can use \n
    ?read=True \n
    ?read=False
    ?title=xyz
    """
    pagination_class = CommonPagination

    def get_queryset(self):
        return PrivateNotification.objects.filter(user=self.request.user).only(
            "body", "is_read", "created_at", "title", "user__first_name", "user__last_name", "notification_type",
            "char_link"
        ).select_related("user")

    def get_permissions(self):
        if self.request.method in SAFE_METHODS or self.request.method == 'PATCH':
            self.permission_classes = (IsAuthenticated,)
        else:
            self.permission_classes = (IsAdminUser,)
        return super().get_permissions()

    def filter_queryset(self, queryset):
        is_read = self.request.query_params.get("read", None)
        title = self.request.query_params.get("title", None)

        if is_read and title:
            queryset = queryset.filter(is_read=is_read, title__icontains=title)
        if is_read:
            queryset = queryset.filter(is_read=is_read)
        if title:
            queryset = queryset.filter(title__icontains=title)
        return queryset

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return serializers.UserNotificationSerializer
        elif self.action == "partial_update":
            return serializers.PatchUserNotificationSerializer
        else:
            return serializers.CreateUserNotificationSerializer


class RequestPhoneView(AsyncAPIView):
    """
    درخواست کد اعتبار سنجی اگر کاربر وجود نداشته باشید کابر رو به همراه پسورد رندوم ان را میسازد
    """
    serializer_class = serializers.AsyncRequestPhoneSerializer
    permission_classes = (AsyncNotAuthenticated,)

    async def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # get phone by serializer
        phone = serializer.validated_data['mobile_phone']

        # generate random password
        random_string = get_random_string(16)

        # استفاده از sync_to_async برای make_password
        hash_password = make_password(password=random_string)

        # get user
        user = await User.objects.filter(mobile_phone=phone).only("id").afirst()
        if user:
            # create otp
            otp = await Otp.objects.acreate(mobile_phone=phone)
        else:
            await User.objects.acreate_user(phone=phone, password=hash_password)
            otp = await Otp.objects.acreate(mobile_phone=phone)

        # send otp sms
        await async_send_otp_sms(phone, otp.code)

        return Response({
            "status": True,
            "message": "code send"
        })


class RequestOtpVerifyView(APIView):
    """
    تایید کد اعتبار سنجی برای ورود به حساب
    """
    serializer_class = serializers.RequestPhoneVerifySerializer
    permission_classes = (NotAuthenticate,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        return Response(
            data={
                "data": data['data'],
                "is_staff": bool(data['is_staff']),
                "is_coach": bool(data['is_coach']),
                "full_name": data['full_name']
            },
            status=HTTP_201_CREATED
        )


class InvitationView(generics.ListAPIView):
    """
    pagination --> 20 item
    لیست کاربران دعوت شده توسط شما
    """
    serializer_class = serializers.InvitationSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = CommonPagination

    def get_queryset(self):
        return Invitation.objects.filter(
            from_student__user=self.request.user
        ).select_related(
            "to_student__user"
        ).only(
            "to_student__user__first_name",
            "to_student__user__last_name",
            # "to_student__referral_code",
            "created_at"
        )
