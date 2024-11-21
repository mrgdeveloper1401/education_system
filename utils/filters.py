from django_filters import FilterSet

from accounts.models import User


class UserFilter(FilterSet):
    class Meta:
        model = User
        fields = {
            "email": ['iexact'],
            "first_name": ["icontains"],
            "last_name": ["icontains"],
            "state__state_name": ['icontains'],
            "city__city": ["icontains"],
            "mobile_phone": ['iexact']
        }
