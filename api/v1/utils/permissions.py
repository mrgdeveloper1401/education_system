from rest_framework import permissions


class CoachAndAdminPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and bool(request.user.is_staff or request.user.is_coach)
