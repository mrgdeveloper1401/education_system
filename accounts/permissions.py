from rest_framework import permissions

from accounts.models import Coach


class IsCoachUser(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_coach:
            return True
        return False
