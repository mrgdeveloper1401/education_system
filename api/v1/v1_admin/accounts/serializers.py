from rest_framework import serializers
from drf_extra_fields.fields import Base64ImageField

from accounts.models import TicketReply


class AdminCreateTicketReplySerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = TicketReply
        fields = ["id", 'message', "image", "ticket"]
        read_only_fields = ['ticket']

    def create(self, validated_data):
        return TicketReply.objects.create(
            sender_id=self.context['request'].user.id,
            ticket_id=self.context['ticket_chat_pk'],
            **validated_data
        )
