from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from accounts.models import User, Otp
from .pagination import UserPagination
from .serializers import UserSerializer, OtpLoginSerializer, VerifyOtpSerializer, UpdateUserSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.select_related("state", "city", "school")
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    pagination_class = UserPagination
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH', "OPTION"]:
            return UpdateUserSerializer
        return super().get_serializer_class()


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
