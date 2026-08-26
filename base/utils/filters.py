from django_filters import FilterSet

from account_app.models import User


class UserFilter(FilterSet):
    class Meta:
        model = User
        fields = {
            "email": ['iexact'],
            "first_name": ["icontains"],
            "last_name": ["icontains"],
            "state__state_name": ['icontains'],
            "city__city": ["icontains"],
            "mobile_phone": ['iexact'],
            "is_active": ["exact"],
        }
