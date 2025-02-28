from rest_framework import permissions

from course.models import AccessCourse


class AccessCoursePermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return bool(AccessCourse.objects.filter(user=request.user, course=obj).exists())


class AccessCourseSectionPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return bool(AccessCourse.objects.filter(user=request.user, course=obj.course).exists())


class AccessSectionFilePermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return bool(AccessCourse.objects.filter(user=request.user, course=obj.section.course).exists())


class AccessSectionVideoPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return bool(AccessCourse.objects.filter(user=request.user, course=obj.section.course).exists())
