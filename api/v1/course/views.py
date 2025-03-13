from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, viewsets, permissions, decorators, response, status, generics
from django.db.models import Prefetch

from course.models import Comment, Section, SectionVideo, SectionFile, Purchases, LessonCourse
from .pagination import CommentPagination
from .paginations import CourseCategoryPagination

from . import serializers


class PurchasesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.PurchasesSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CourseCategoryPagination

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="The name of the purchase.",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        res = super().list(request, *args, **kwargs)
        return res

    def get_queryset(self):
        query = Purchases.objects.filter(user=self.request.user).select_related("course", "coach__user").only(
            "id", "course__course_name", "course__course_image", "coach__user__first_name", "coach__user__last_name",
            "course__project_counter"
        )
        course_name = self.request.query_params.get("name")

        if course_name:
            query = query.filter(course__course_name__icontains=course_name)
        elif course_name:
            query = query.filter(course__course_name__icontains=course_name)
        return query

    @decorators.action(detail=True, methods=["GET"])
    def sections(self, request, pk=None):
        purchase = self.get_object()
        sections = Section.objects.filter(course=purchase.course).only(
            'id', "title", "created_at", "cover_image"
        )
        serializer = serializers.CourseSectionSerializer(sections, many=True)
        return response.Response(serializer.data)

    @decorators.action(detail=True, methods=['GET'], url_path='sections/(?P<section_pk>[^/.]+)')
    def section_detail(self, request, pk=None, section_pk=None):
        purchase = self.get_object()
        try:
            section = Section.objects.filter(id=section_pk, course=purchase.course).only(
                "id", "title", "created_at", "cover_image"
            ).first()
            serializer = serializers.CourseSectionSerializer(section)
            return response.Response(serializer.data)
        except Section.DoesNotExist:
            return response.Response({"detail": "Section not found."}, status=status.HTTP_404_NOT_FOUND)

    @decorators.action(detail=True, methods=['GET'], url_path="sections/(?P<section_pk>[^/.]+)/videos")
    def section_video(self, request, pk=None, section_pk=None):
        purchase = self.get_object()
        section_video = SectionVideo.objects.filter(section_id=section_pk, section__course=purchase.course).only(
            "id", "video", "created_at"
        )
        serializer = serializers.CourseSectionVideoSerializer(section_video, many=True)
        return response.Response(serializer.data)

    @decorators.action(
        detail=True,
        methods=['GET'],
        url_path="sections/(?P<section_pk>[^/.]+)/videos/(?P<section_video_pk>[^/.]+)"
    )
    def section_video_detail(self, request, section_video_pk, pk=None, section_pk=None):
        purchase = self.get_object()
        try:
            section_video = SectionVideo.objects.filter(
                section_id=section_pk,
                id=section_video_pk,
                section__course=purchase.course
            ).only("id", "video", "created_at").first()
            serializer = serializers.CourseSectionVideoSerializer(section_video)
            return response.Response(serializer.data)
        except SectionVideo.DoesNotExist:
            return response.Response({"detail": "Section video not found."}, status=status.HTTP_404_NOT_FOUND)

    @decorators.action(
        detail=True,
        methods=['GET'],
        url_path='sections/(?P<section_pk>[^/.]+)/files'
    )
    def section_file(self, request, pk=None, section_pk=None):
        purchase = self.get_object()
        section_file = SectionFile.objects.filter(section_id=section_pk, section__course=purchase.course).only(
            "id", "zip_file", "created_at", "is_close", "title"
        )
        serializer = serializers.CourseSectionFileSerializer(section_file, many=True)
        return response.Response(serializer.data)

    @decorators.action(
        detail=True,
        methods=['GET'],
        url_path='sections/(?P<section_pk>[^/.]+)/files/(?P<section_file_pk>[^/.]+)'
    )
    def section_file_detail(self, request, pk=None, section_pk=None, section_file_pk=None):
        purchase = self.get_object()
        try:
            section_file = SectionFile.objects.filter(
                id=section_file_pk,
                section_id=section_pk,
                section__course=purchase.course
            ).only(
                "id", "zip_file", "created_at", "is_close", "title"
            ).first()
            serializer = serializers.CourseSectionFileSerializer(section_file)
            return response.Response(serializer.data)
        except SectionFile.DoesNotExist:
            return response.Response({"detail": "Section video not found."}, status=status.HTTP_404_NOT_FOUND)


class CommentViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin,
                     viewsets.GenericViewSet):
    serializer_class = serializers.CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CommentPagination

    def get_queryset(self):
        return Comment.objects.filter(course_id=self.kwargs['course_pk'])

    def get_serializer_context(self):
        return {
            "user": self.request.user,
            "course_pk": self.kwargs["course_pk"]
        }


class LessonCourseFinishedApiView(generics.ListAPIView):
    serializer_class = serializers.LessonCourseFinishedSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        query = LessonCourse.objects.filter(
            students__user=self.request.user
        ).select_related(
            "course", "coach__user"
        ).only(
            "course__course_name", "course__course_image", "progress", "coach__user__first_name",
            "coach__user__last_name", "course__project_counter"
        )
        progress_status = self.request.query_params.get("status")
        if progress_status:
            query = query.filter(progress__exact=progress_status)
        return query
