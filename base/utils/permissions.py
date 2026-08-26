from rest_framework import permissions
from django.utils import timezone

# from course.models import Quiz


class NotAuthenticate(permissions.BasePermission):
    message = 'کاربر احراز شده نمیتواند دسترسی داشته باشد'

    def has_permission(self, request, view):
        return not request.user.is_authenticated


class CoursePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True


class StudentPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and hasattr(request.user, 'student'):
            return True


class CoachPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated and hasattr(request.user, 'coach'):
            return True


class EditScorePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_authenticated and hasattr(request.user, 'coach'):
            return True


class CommentPermission(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if obj.student.user == request.user:
            return True


class PracticePermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        if hasattr(request.user, "coach"):
            return True


class SubmitPracticePermissions(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        if obj.student.user == request.user:
            return True


class QuizPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return hasattr(request.user, 'coach')

    def has_object_permission(self, request, view, obj):
        if obj.coach.user == request.user:
            return True


# class QuestionPermission(permissions.BasePermission):
#     def has_permission(self, request, view):
#         quiz_pk = view.kwargs['quiz_pk']
#         try:
#             quiz = Quiz.objects.select_related("coach__user").get(pk=quiz_pk)
#         except Quiz.DoesNotExist:
#             return False
#         if not request.user.is_authenticated:
#             return False
#         if quiz.coach.user == request.user:
#             return True
#         return timezone.now() > quiz.quiz_time

    def has_object_permission(self, request, view, obj):
        if hasattr(request.user, 'coach') and obj.quiz.coach.user == request.user:
            return True
