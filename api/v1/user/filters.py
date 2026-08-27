from django_filters.rest_framework import FilterSet

from apps.account_app.models import TicketRoom

class TicketRoomFilter(FilterSet):
    class Meta:
        model = TicketRoom
        fields = (
            "is_close",
        )
