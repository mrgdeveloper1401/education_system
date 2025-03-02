from rest_framework import viewsets, permissions, exceptions, generics, filters
from django.db.models import Prefetch

from accounts.models import Coach
from . import serializers
from course.models import Category, Course, Section, SectionFile, SectionVideo, CoachEnrollment, StudentEnrollment
from .paginations import AdminPagination, AdminStudentByCoachPagination


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = Category.objects.only("id", "category_name")
    pagination_class = AdminPagination

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.CreateCategorySerializer
        if self.action in ["list", "retrieve"]:
            return serializers.ListRetrieveCategorySerializer
        if self.action in ['update', 'partial_update']:
            return serializers.UpdateCategoryNodeSerializer
        if self.action == "destroy":
            return serializers.ListRetrieveCategorySerializer
        else:
            raise exceptions.NotAcceptable


class AdminCourseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    pagination_class = AdminPagination

    def get_queryset(self):
        return Course.objects.filter(category_id=self.kwargs["category_pk"]).defer("deleted_at", "is_deleted")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['category_pk'] = self.kwargs["category_pk"]
        return context

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.AdminListCourseSerializer
        if self.action == "create":
            return serializers.AdminCreateCourseSerializer
        if self.action in ['update', 'partial_update', "retrieve", "destroy"]:
            return serializers.AdminUpdateCourseSerializer
        else:
            raise exceptions.NotAcceptable


class AdminCourseSectionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    pagination_class = AdminPagination

    def get_queryset(self):
        return Section.objects.filter(course_id=self.kwargs["course_pk"]).defer("deleted_at", "is_deleted")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["course_pk"] = self.kwargs["course_pk"]
        return context

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.AdminCreateCourseSectionSerializer
        else:
            return serializers.AdminListCourseSectionSerializer


class AdminSectionFileViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.AdminCreateCourseSectionFileSerializer
        else:
            return serializers.AdminListCourseSectionFileSerializer

    def get_queryset(self):
        return SectionFile.objects.filter(section_id=self.kwargs["section_pk"]).only(
            "id", "created_at", "updated_at", "zip_file", "section_id", "is_publish", "title", "is_close",
            "expired_data"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['section_pk'] = self.kwargs['section_pk']
        return context


class AdminSectionVideoViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.AdminCreateSectionVideoSerializer
        else:
            return serializers.AdminListSectionVideoSerializer

    def get_queryset(self):
        return SectionVideo.objects.filter(section_id=self.kwargs["section_pk"]).only(
            "id", "created_at", "updated_at", "video", "section_id", "is_publish"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['section_pk'] = self.kwargs['section_pk']
        return context


class AdminCourseListApiView(generics.ListAPIView):
    queryset = Course.objects.only('id', "course_name")
    serializer_class = serializers.AdminCourseListSerializer
    permission_classes = [permissions.IsAdminUser]
    search_fields = ['course_name']
    filter_backends = [filters.SearchFilter]


class AdminCoachViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AdminCoachSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = AdminPagination

    def get_queryset(self):
        return CoachEnrollment.objects.filter(course_id=self.kwargs['course_pk']).only(
            'id', "is_active", "coach_id"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['course_pk'] = self.kwargs['course_pk']
        return context


class AdminStudentEnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AdminStudentSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = AdminPagination

    def get_queryset(self):
        return StudentEnrollment.objects.filter(course_id=self.kwargs['course_pk']).only("id", "student_id", "coach_id")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['course_pk'] = self.kwargs['course_pk']
        return context


class AdminStudentByCoachApiView(generics.ListAPIView):
    serializer_class = serializers.AdminGetStudentByCoachSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = AdminStudentByCoachPagination

    def get_queryset(self):
        return (StudentEnrollment.objects.only("student").
                filter(course_id=self.kwargs['course_pk'], coach_id=self.kwargs['coach_pk']))
