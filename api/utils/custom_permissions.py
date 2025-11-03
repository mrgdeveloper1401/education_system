from rest_framework.permissions import BasePermission


class AsyncNotAuthenticated(BasePermission):
    message = 'کاربر احراز شده نمیتواند دسترسی داشته باشد'

    async def has_permission(self, request, view):
        return not request.user.is_authenticated
