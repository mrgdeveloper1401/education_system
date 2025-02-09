from rest_framework import permissions

from subscription_app.models import AccessCourse


class AccessCoursePermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return AccessCourse.objects.filter(user=request.user, course=obj, is_active=True).exists()


class AccessCourseSectionPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return AccessCourse.objects.filter(user=request.user, course=obj.course, is_active=True).exists()


class AccessCourseSectionImagePermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return AccessCourse.objects.filter(user=request.user, course=obj.section.course, is_active=True).exists()
