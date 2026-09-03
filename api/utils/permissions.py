from rest_framework.permissions import BasePermission


class AsyncNotAuthenticated(BasePermission):
    message = "کاربر احراز شده نمیتواند دسترسی داشته باشد"

    async def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsCoachUser(BasePermission):
    def has_permission(self, request, view):
        if (request.user and request.user.is_authenticated) and (
            request.user.is_coach or request.user.is_staff
        ):
            return True
        return False
