from django_filters.rest_framework import filterset

from apps.advertise_app.models import ConsultationSlot


class AdvertiseFilter(filterset.FilterSet):
    class Meta:
        model = ConsultationSlot
        fields = {
            "is_available": ("exact",),
        }
