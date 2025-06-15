from rest_framework import permissions

from accounts.models import Coach


class IsCoachUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if (request.user and request.user.is_authenticated) and (request.user.is_coach or request.user.is_staff):
            return True
        return False
