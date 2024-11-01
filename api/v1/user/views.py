from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin
from django.utils.translation import gettext_lazy as _

from .serializers import UserSerializer, OtpVerifySerializer, ResendOtpCodeSerializer
from accounts.models import User


class CreateUserViewSet(CreateModelMixin, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class OtpVerifyApiView(APIView):
    serializer_class = OtpVerifySerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            data={
                "access": serializer.validated_data['access'],
                'refresh': serializer.validated_data['refresh'],
                "message": _("شما با موفقیت وارد حساب خود شدید")
            },
            status=HTTP_200_OK
        )


class ResendOtpCodeApiView(APIView):
    serializer_class = ResendOtpCodeSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": _("کد ورود مجدد برای شما ارسال خواهد شد")})
