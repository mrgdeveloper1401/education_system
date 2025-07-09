from rest_framework import permissions

from course.models import StudentAccessSection


class IsCoachPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool((request.user and request.user.is_authenticated) and request.user.is_coach)


class IsAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        print(view)
        section_pk = view.kwargs.get('section_pk')

        has_access = True

        if section_pk:
            has_access = StudentAccessSection.objects.filter(
                section_id=section_pk,
                student__user=request.user,
                is_access=True
            ).exists()
        return has_access


class IsOwnerOrReadOnly(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):
        return bool(obj.user == request.user)
