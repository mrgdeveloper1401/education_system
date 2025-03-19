from rest_framework import viewsets, generics, permissions
from rest_framework import filters

from accounts.models import TicketReply, BestStudent, Student, Coach, User
from . import serializers
from .pagination import BestStudentPagination


class TicketReplyViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AdminCreateTicketReplySerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = TicketReply.objects.filter(is_active=True).only(
        "message", "image", "ticket", "id", "created_at"
    )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['ticket_chat_pk'] = self.kwargs['ticket_chat_pk']
        return context


class AdminBestStudentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    pagination_class = BestStudentPagination
    serializer_class = serializers.AdminBestStudentSerializer
    queryset = BestStudent.objects.only(
        "id", "is_publish", "description", "attributes", "student_image", "student"
    )


class AdminStudentApiView(generics.ListAPIView):
    serializer_class = serializers.AdminStudentListSerializer
    permission_classes = [permissions.IsAdminUser]
    queryset = Student.objects.only(
        "id", "user__first_name", "user__last_name",  "user__mobile_phone"
    ).select_related(
        "user"
    ).filter(is_active=True)
    search_fields = ['user__mobile_phone']
    filter_backends = [filters.SearchFilter]


class AdminCoachApiView(generics.ListAPIView):
    queryset = Coach.objects.select_related("user").only(
        "id", "user__first_name", "user__last_name", "user__mobile_phone"
    ).filter(is_active=True)
    serializer_class = serializers.AdminCouchListSerializer
    permission_classes = [permissions.IsAdminUser]
    search_fields = ['user__mobile_phone']
    filter_backends = [filters.SearchFilter]


class AdminUserApiView(generics.ListAPIView):
    queryset = User.objects.filter(is_active=True).only('id', "mobile_phone", "first_name", "last_name")
    serializer_class = serializers.AdminUserListSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        query = super().get_queryset()
        phone = self.request.query_params.get("phone")
        if phone:
            query = query.filter(mobile_phone__icontains=phone)
        return query
