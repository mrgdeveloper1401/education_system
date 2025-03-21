from django.db.models import Prefetch
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, viewsets, permissions, decorators, response, status, exceptions, generics

from accounts.models import Student
from course.models import Comment, Section, SectionVideo, SectionFile, LessonCourse, StudentSectionScore, \
    PresentAbsent, StudentAccessSection, SendSectionFile
from .pagination import CommentPagination
from .paginations import CourseCategoryPagination

from . import serializers
from .permissions import IsCoachPermission, CoachPermissionOrReadOnly


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
        query = LessonCourse.objects.filter(
            students__user=self.request.user, is_active=True, course__is_deleted=False
        ).select_related(
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

    @extend_schema(
        responses={200: serializers.StudentAccessSectionSerializer(many=True)}
    )
    @decorators.action(detail=True, methods=["GET"])
    def sections(self, request, pk=None):
        lesson_course = self.get_object()
        sections = StudentAccessSection.objects.filter(
            section__course=lesson_course.course, student__user=request.user, section__is_publish=True
        ).only(
            "section__cover_image", "section__title", 'is_access'
        ).select_related("section")
        serializer = serializers.StudentAccessSectionSerializer(sections, many=True)
        return response.Response(serializer.data)

    @extend_schema(
        responses={200: serializers.StudentAccessSectionDetailSerializer}
    )
    @decorators.action(detail=True, methods=['GET'], url_path='sections/(?P<section_pk>[^/.]+)')
    def section_detail(self, request, pk=None, section_pk=None):
        lesson_course = self.get_object()
        section = (StudentAccessSection.objects.filter(
            section__course=lesson_course.course, student__user=request.user, section_id=section_pk,
            section__is_publish=True
        ).only('section__created_at', "section__cover_image", "section__title", "section__description", "is_access").
                   select_related("section").first())

        if not section:
            raise exceptions.NotFound()

        if section.is_access is False and request.user.student:
            raise exceptions.PermissionDenied("you do not view this section")

        serializer = serializers.StudentAccessSectionDetailSerializer(section)
        return response.Response(serializer.data)

    @extend_schema(
        responses={200: serializers.CourseSectionFileSerializer}
    )
    @decorators.action(detail=True, methods=['GET'], url_path='sections/(?P<section_pk>[^/.]+)/section_file')
    def section_file(self, request, pk=None, section_pk=None):
        lesson_course = self.get_object()
        section_file = SectionFile.objects.filter(
            section_id=section_pk, section__course=lesson_course.course, is_publish=True,
            section__is_publish=True
        ).only("zip_file", "title")
        serializer = serializers.CourseSectionFileSerializer(section_file, many=True)
        return response.Response(serializer.data)

    @extend_schema(
        responses={
            200: serializers.CourseSectionVideoSerializer
        }
    )
    @decorators.action(detail=True, methods=['GET'], url_path="sections/(?P<section_pk>[^/.]+)/videos")
    def section_video(self, request, pk=None, section_pk=None):
        section_video = SectionVideo.objects.filter(
            section_id=section_pk, is_publish=True, section__is_publish=True
        ).only("video", "title", "section__cover_image")
        serializer = serializers.CourseSectionVideoSerializer(section_video, many=True)
        return response.Response(serializer.data)

    @extend_schema(
        responses={
            200: serializers.SectionScoreSerializer
        }
    )
    @decorators.action(
        detail=True,
        methods=['GET'],
        url_path='sections/(?P<section_pk>[^/.]+)/score')
    def section_score(self, request, pk=None, section_pk=None):
        lesson_course = self.get_object()
        score = StudentSectionScore.objects.filter(
            section_id=section_pk, section__course=lesson_course.course, student__user=request.user,
            section__is_publish=True
        ).only(
            "score"
        )
        serializer = serializers.SectionScoreSerializer(score, many=True)
        return response.Response(serializer.data)

    @extend_schema(
        responses={
            200: serializers.StudentPresentAbsentSerializer
        }
    )
    @decorators.action(detail=True, methods=['GET'], url_path="sections/(?P<section_pk>[^/.]+)/present_absent")
    def section_present_absent(self, request, pk=None, section_pk=None):
        present_absent = PresentAbsent.objects.filter(
            section_id=section_pk, student__user=request.user, section__is_publish=True
        ).only("is_present")
        serializer = serializers.StudentPresentAbsentSerializer(present_absent, many=True)
        return response.Response(serializer.data)


class StudentLessonCourseViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsCoachPermission]
    serializer_class = serializers.StudentLessonCourseSerializer

    def get_queryset(self):
        return LessonCourse.objects.filter(id=self.kwargs['lesson_course_pk']).only(
            "students"
        ).prefetch_related(
            Prefetch("students", Student.objects.filter(is_active=True).select_related("user").only(
                "student_number", "user__first_name", "user__last_name"
            ))
        )


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


class StudentSendfileViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.SendFileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SendSectionFile.objects.filter(student__user=self.request.user).only(
            "section_file", "score", "description", "zip_file"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        if "pk" in self.kwargs:
            context['section_file_pk'] = self.kwargs['pk']
        return context

    @extend_schema(
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "section_file": {"type": "integer", "format": "int32"},
                    "description": {"type": "string", "format": "string"},
                    "zip_file": {"type": "string", "format": "binary"},
                }
            }
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class StudentSectionFileApiView(generics.ListAPIView):
    serializer_class = serializers.StudentSectionFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = SectionFile.objects.filter(is_publish=True).only(
        "id", "title"
    )
