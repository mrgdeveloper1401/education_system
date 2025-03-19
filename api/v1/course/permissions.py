from rest_framework import permissions


class IsCoachPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool((request.user and request.user.is_authenticated) and request.user.is_coach)


class CoachPermissionOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            return bool(request.user.is_coach)
