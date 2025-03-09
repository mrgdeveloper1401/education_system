from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import CSRFCheck
from rest_framework import exceptions

from education_system import base


def enforce_csrf(request):
    def dumpy_get_response():
        return None

    check = CSRFCheck(dumpy_get_response)
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        raise exceptions.PermissionDenied("csrf Failed %s" % reason)


class CustomAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)

        if not header:
            raw_token = request.COOKIES.get(base.SIMPLE_JWT['AUTH_COOKIE']) or None
        else:
            raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validate_token = self.get_validated_token(raw_token)
        enforce_csrf(request)
        return self.get_user(validate_token), validate_token
