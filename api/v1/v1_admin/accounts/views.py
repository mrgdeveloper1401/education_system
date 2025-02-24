from rest_framework import viewsets, generics, permissions

from accounts.models import TicketReply, BestStudent, Student
from . import serializers
from .pagination import BestStudentPagination, ListStudentByIdPagination


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
    queryset = Student.objects.only("id", "user__first_name", "user__last_name").select_related(
        "user"
    )
    pagination_class = ListStudentByIdPagination
