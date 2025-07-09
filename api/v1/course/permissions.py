from rest_framework import permissions

from course.models import StudentAccessSection


class IsCoachPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool((request.user and request.user.is_authenticated) and request.user.is_coach)


class IsAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        # print(view) # api.v1.course.views.PurchasesViewSet object at 0x7fd824198d10>
        # print(view.kwargs) # {'pk': '1', 'section_pk': '1'}
        section_pk = view.kwargs.get('section_pk')

        has_access = True

        if section_pk:
            has_access = StudentAccessSection.objects.filter(
                section_id=section_pk,
                student__user_id=request.user.id,
                is_access=True
            ).only("id").exists()
        return has_access


class IsOwnerOrReadOnly(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):

        # print(view) # <api.v1.course.views.CommentViewSet object at 0x7fa4c922a3d0>

        # print(obj) Comment object (4)

        if request.method in permissions.SAFE_METHODS:
            return True

        return bool(obj.user == request.user)
