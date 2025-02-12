from rest_framework import permissions


class TicketRoomPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if obj.sender == request.user:
            return True
        return False
