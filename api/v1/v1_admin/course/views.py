from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import viewsets, permissions, exceptions, generics, filters

from . import serializers
from course.models import Category, Course, Section, SectionFile, SectionVideo, LessonCourse, Certificate, \
    StudentSectionScore
from .paginations import AdminPagination


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
            "id", "created_at", "updated_at", "video", "section_id", "is_publish", "title"
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


class AdminLessonCourseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    serializer_class = serializers.AdminLessonCourseSerializer
    pagination_class = AdminPagination

    def get_queryset(self):
        query = LessonCourse.objects.filter(course_id=self.kwargs['course_pk']).prefetch_related("students").defer(
            "is_deleted", "deleted_at"
        )
        progress = self.request.query_params.get('progress')
        if progress:
            query = query.filter(progress=progress)
        return query

    @extend_schema(
        parameters=[OpenApiParameter(
            name="progress",
            type=OpenApiTypes.STR,
            location=OpenApiParameter.QUERY,
            description="search in progress class room fields [not_started, finished, in_progress]"
        )]
    )
    def list(self, request, *args, **kwargs):
        res = super().list(request, *args, **kwargs)
        return res


class AdminCertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.defer("deleted_at", "is_deleted", "created_at", "updated_at")
    serializer_class = serializers.AdminCertificateSerializer
    permission_classes = [permissions.IsAdminUser]
