from rest_framework import permissions

from accounts.models import Coach
from course.models import StudentAccessCourse, CoachAccessCourse


class StudentAccessCoursePermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        is_coach = getattr(request.user, "coach", None)
        if is_coach:
            return CoachAccessCourse.objects.filter(coach__user=request.user, course=obj, is_active=True).exists()
        else:
            return StudentAccessCourse.objects.filter(student__user=request.user, course=obj, is_active=True).exists()


class StudentAccessCourseSectionPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        is_coach = getattr(request.user, "coach", None)
        if is_coach:
            return bool(CoachAccessCourse.objects.filter(coach__user=request.user, course=obj.course, is_active=True))
        else:
            return bool(StudentAccessCourse.objects.filter(student__user=request.user, course=obj.course,
                                                           is_active=True))


class StudentAccessCourseSectionFilePermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        is_coach = getattr(request.user, "coach", None)
        if is_coach:
            return bool(CoachAccessCourse.objects.filter(coach__user=request.user, course=obj.section.course,
                                                         is_active=True))
        else:
            return bool(StudentAccessCourse.objects.filter(student__user=request.user, course=obj.section.course,
                                                           is_active=True))


class StudentAccessCourseSendSectionFilePermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        is_coach = getattr(request.user, "coach", None)
        if is_coach:
            return bool(CoachAccessCourse.objects.filter(coach__user=request.user,
                                                         course=obj.section_file.section.course,
                                                         is_active=True))
        else:
            return bool(StudentAccessCourse.objects.filter(student__user=request.user,
                                                           course=obj.section_file.section.course,
                                                           is_active=True))


class IsCoachAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return Coach.objects.filter(user=request.user).exists()
