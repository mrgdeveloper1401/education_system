from rest_framework import viewsets
from rest_framework import permissions
from accounts.models import TicketReply
from . import serializers


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
