from rest_framework import permissions


class AccessCourse(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        course_access = request.user.access_user.values_list("course_id", flat=True)
        if obj.id in course_access:
            return True
        return False


class AccessSection(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        course_access = request.user.access_user.values_list("course_id", flat=True)
        if obj.course.id in course_access:
            return True
        return False
