from rest_framework import viewsets
from rest_framework import permissions
from accounts.models import TicketReply, BestStudent, BestStudentAttribute
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

    def get_queryset(self):
        return BestStudent.objects.select_related("student__user").only(
            "id", "student__user__first_name", "student__user__last_name", "is_publish", "created_at", "description"
        )

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.AdminCreateBestStudentSerializer
        else:
            return serializers.AdminListBestStudentSerializer


class AdminBestStudentAttributeViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.AdminCreateBestStudentAttributeSerializer
        else:
            return serializers.AdminListBestStudentAttributeSerializer

    def get_queryset(self):
        return BestStudentAttribute.objects.filter(best_student_id=self.kwargs["best_student_pk"]).only(
            "id", "best_student_id", 'attribute', "is_active", "created_at"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['best_student_pk'] = self.kwargs['best_student_pk']
        return context
