from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser

from accounts.models import User
from .pagination import UserPagination
from .serializers import UserSerializer


class UserViewSet(ModelViewSet):
    queryset = User.objects.select_related("state", "city", "school")
    serializer_class = UserSerializer
    permission_classes = [IsAdminUser]
    pagination_class = UserPagination
