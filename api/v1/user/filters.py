from django_filters.rest_framework import FilterSet

from accounts.models import TicketRoom

class TicketRoomFilter(FilterSet):
    class Meta:
        model = TicketRoom
        fields = (
            "is_close",
        )
