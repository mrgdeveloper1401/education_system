from rest_framework.permissions import BasePermission


class NotAuthenticate(BasePermission):
    message = 'کاربر احراز شده نمیتواند دسترسی داشته باشد'

    def has_permission(self, request, view):
        return not request.user.is_authenticated
