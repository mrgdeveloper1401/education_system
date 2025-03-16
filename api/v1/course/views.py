from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, viewsets, permissions, decorators, response, status

from course.models import Comment, Section, SectionVideo, SectionFile, LessonCourse, SectionScore
from .pagination import CommentPagination
from .paginations import CourseCategoryPagination

from . import serializers


class PurchasesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.LessonCourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CourseCategoryPagination

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="class_name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="The name of the purchase.",
            ),
            OpenApiParameter(
                name="progress_lesson",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="The name of the progress lesson.",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        res = super().list(request, *args, **kwargs)
        return res

    def get_queryset(self):
        query = LessonCourse.objects.filter(students__user=self.request.user, is_active=True).select_related(
            "course", "coach__user"
        ).only(
            "course__course_name", "course__course_image", "course__project_counter", "coach__user__last_name",
            "coach__user__first_name", "progress", "class_name"
        )
        class_name = self.request.query_params.get("class_name")
        progress_lesson = self.request.query_params.get("progress_lesson")

        if class_name and progress_lesson:
            query = query.filter(class_name__icontains=class_name, progress__exact=progress_lesson)
        elif class_name:
            query = query.filter(class_name__icontains=class_name)
        elif progress_lesson:
            query = query.filter(progress__exact=progress_lesson)
        else:
            query = query
        return query

    @decorators.action(detail=True, methods=["GET"])
    def sections(self, request, pk=None):
        lesson_course = self.get_object()
        sections = Section.objects.filter(course=lesson_course.course).only(
            'id', "title", "created_at", "cover_image"
        )
        serializer = serializers.CourseSectionSerializer(sections, many=True)
        return response.Response(serializer.data)

    @decorators.action(detail=True, methods=['GET'], url_path='sections/(?P<section_pk>[^/.]+)')
    def section_detail(self, request, pk=None, section_pk=None):
        lesson_course = self.get_object()
        try:
            section = Section.objects.filter(id=section_pk, course=lesson_course.course).only(
                "id", "title", "created_at", "cover_image"
            ).first()
            serializer = serializers.CourseSectionSerializer(section)
            return response.Response(serializer.data)
        except Section.DoesNotExist:
            return response.Response({"detail": "Section not found."}, status=status.HTTP_404_NOT_FOUND)

    @decorators.action(detail=True, methods=['GET'], url_path="sections/(?P<section_pk>[^/.]+)/videos")
    def section_video(self, request, pk=None, section_pk=None):
        lesson_course = self.get_object()
        section_video = SectionVideo.objects.filter(section_id=section_pk, section__course=lesson_course.course).only(
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
        lesson_course = self.get_object()
        try:
            section_video = SectionVideo.objects.filter(
                section_id=section_pk,
                id=section_video_pk,
                section__course=lesson_course.course
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
        lesson_course = self.get_object()
        section_file = SectionFile.objects.filter(section_id=section_pk, section__course=lesson_course.course).only(
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
        lesson_course = self.get_object()
        try:
            section_file = SectionFile.objects.filter(
                id=section_file_pk,
                section_id=section_pk,
                section__course=lesson_course.course
            ).only(
                "id", "zip_file", "created_at", "is_close", "title"
            ).first()
            serializer = serializers.CourseSectionFileSerializer(section_file)
            return response.Response(serializer.data)
        except SectionFile.DoesNotExist:
            return response.Response({"detail": "Section video not found."}, status=status.HTTP_404_NOT_FOUND)

    @decorators.action(
        detail=True,
        methods=['GET'],
        url_path='sections/(?P<section_pk>[^/.]+)/files/(?P<section_file_pk>[^/.]+)/section_score'
    )
    def section_file_score(self, request, pk=None, section_pk=None, section_file_pk=None):
        section_score = SectionScore.objects.filter(
            section_file_id=self.kwargs['section_file_pk'],
            section_file__section_id=self.kwargs['section_pk'],
        ).only("id", "section_file", "score")
        serializer = serializers.SectionScoreSerializer(section_score, many=True)
        return response.Response(serializer.data)

    @decorators.action(
        detail=True,
        methods=['GET'],
        url_path='sections/(?P<section_pk>[^/.]+)/files/(?P<section_file_pk>[^/.]+)/section_score/'
                 '(?P<section_score_pk>[^/.]+)'
    )
    def section_file_score_detail(self, request, pk=None, section_pk=None, section_file_pk=None, section_score_pk=None):
        section_score = SectionScore.objects.filter(
            section_file_id=self.kwargs['section_file_pk'],
            section_file__section_id=self.kwargs['section_pk'],
            id=section_score_pk
        ).only("id", "section_file", "score").first()
        serializer = serializers.SectionScoreSerializer(section_score)
        return response.Response(serializer.data)


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
