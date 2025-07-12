from rest_framework import viewsets, generics, permissions

from accounts.models import BestStudent, Student, Coach, User
from utils.pagination import CommonPagination
from . import serializers
from ...utils.permissions import CoachAndAdminPermission


class AdminBestStudentViewSet(viewsets.ModelViewSet):
    """
    api admin the best student
    pagination --> 20 item
    permission --? only amdin user
    """
    permission_classes = (permissions.IsAdminUser,)
    pagination_class = CommonPagination
    serializer_class = serializers.AdminBestStudentSerializer
    queryset = BestStudent.objects.only(
        "is_publish", "description", "attributes", "student_image", "student"
    )


class AdminStudentApiView(generics.ListAPIView):
    """
    api admin the student list
    permission --? only admin user
    filter query --> ?phone=phone_number
    """
    serializer_class = serializers.AdminStudentListSerializer
    permission_classes = (permissions.IsAdminUser,)
    queryset = Student.objects.only(
        "user__first_name", "user__last_name",  "user__mobile_phone", "is_active"
    ).select_related(
        "user"
    )

    def filter_queryset(self, queryset):
        phone = self.request.query_params.get("phone", None)

        if phone:
            return queryset.filter(user__mobile_phone__icontains=phone)
        else:
            return queryset


class AdminCoachApiView(generics.ListAPIView):
    """
    show list coach \n
    permission --> only admin user \n
    search field --> use mobile phon (?mobile_phone=phone_number)
    """
    queryset = Coach.objects.filter(is_active=True).select_related("user").only(
        "user__first_name", "user__last_name", "user__mobile_phone"
    )
    serializer_class = serializers.AdminCouchListSerializer
    permission_classes = (CoachAndAdminPermission,)

    def filter_queryset(self, queryset):
        phone = self.request.query_params.get("mobile_phone", None)

        if phone:
            return queryset.filter(user__mobile_phone__contains=phone)
        else:
            return queryset


# class AdminUserApiView(generics.ListAPIView):
    # """
    # show list user
    # permission --> admin
    # filter query --> ?phone=phone_number
    # """
    # queryset = User.objects.only("mobile_phone", "first_name", "last_name", "is_coach", "is_active")
    # serializer_class = serializers.AdminUserListSerializer
    # permission_classes = (permissions.IsAdminUser,)
    #
    # def filter_queryset(self, queryset):
    #     phone = self.request.query_params.get("phone", None)
    #
    #     if phone:
    #         return queryset.filter(mobile_phone__icontains=phone)
    #     else:
    #         return queryset
