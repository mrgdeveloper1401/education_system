from rest_framework import permissions


class NotAuthenticate(permissions.BasePermission):
    message = 'کاربر احراز شده نمیتواند دسترسی داشته باشد'

    def has_permission(self, request, view):
        return not request.user.is_authenticated


class CoursePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

    # def has_object_permission(self, request, view, obj):
    #     if request.user in obj.coach:
    #         return True
