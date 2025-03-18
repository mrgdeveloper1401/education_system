from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, viewsets, permissions, decorators, response, status, exceptions
from guardian.shortcuts import get_objects_for_user

from course.models import Comment, Section, SectionVideo, SectionFile, LessonCourse, StudentSectionScore, \
    PresentAbsent
from .pagination import CommentPagination
from .paginations import CourseCategoryPagination

from . import serializers
from .permissions import IsCoachPermission


class PurchasesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.LessonCourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CourseCategoryPagination

    def get_serializer_class(self):
        if self.action == "section_score" and self.request.method == "POST":
            return serializers.CreateUpdateSectionScoreSerializer
        elif self.action == "detail_section_score":
            return serializers.CreateUpdateSectionScoreSerializer
        elif self.action == 'grant_access':
            return serializers.LessonCourseStudentSerializer
        else:
            return super().get_serializer_class()

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
        is_coach = getattr(self.request.user, "is_coach", False)

        if is_coach:
            query = LessonCourse.objects.filter(coach__user=self.request.user, is_active=True).select_related(
                "course", "coach__user"
            ).only(
                "course__course_name", "course__course_image", "course__project_counter", "coach__user__last_name",
                "coach__user__first_name", "progress", "class_name"
            )
        else:
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

    @decorators.action(detail=True, methods=['GET', "POST"], url_path="sections/(?P<section_pk>[^/.]+)/access")
    def grant_access(self, request, pk=None, section_pk=None):

        is_coach = getattr(self.request.user, "is_coach", False)
        ser_data = serializers.LessonCourseStudentSerializer

        if not is_coach:
            raise exceptions.PermissionDenied("you do not have permission this per view action")

        if request.method == "POST":
            serializer = ser_data(data=request.data, context={"section_pk": section_pk})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "GET":
            serializer = ser_data()
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        else:
            raise exceptions.NotAcceptable()

    @decorators.action(detail=True, methods=["GET", 'POST'], url_path="sections/(?P<section_pk>[^/.]+)/score")
    def section_score(self, request, pk=None, section_pk=None):
        is_coach = getattr(self.request.user, "is_coach", False)

        if request.method == "GET":
            lesson_course = self.get_object()

            section_score = StudentSectionScore.objects.filter(
                section_id=self.kwargs['section_pk'], section__course=lesson_course.course
            ).only('id', "section", "score")
            serializer = serializers.SectionScoreSerializer(section_score, many=True)
            return response.Response(serializer.data)
        elif request.method == "POST":
            if not is_coach:
                raise exceptions.PermissionDenied("you do not have permission to perform this action")

            serializer = serializers.CreateUpdateSectionScoreSerializer(
                data=request.data,
                context={"section_pk": self.kwargs['section_pk']}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise exceptions.NotAcceptable()

    @decorators.action(
        detail=True, 
        methods=["GET", "PATCH"], 
        url_path="sections/(?P<section_pk>[^/.]+)/score/(?P<score_pk>[^/.]+)"
    )
    def detail_section_score(self, request, pk=None, section_pk=None, score_pk=None):
        score = StudentSectionScore.objects.filter(id=score_pk).only('id', "section", "score").first()
        if request.method == "GET":
            serializer = serializers.SectionScoreSerializer(score)
            return response.Response(serializer.data)

        elif request.method == "PATCH":
            is_coach = getattr(request.user, "coach", False)
            if not is_coach:
                raise exceptions.PermissionDenied("you do not have permission to perform this action")
            serializer = serializers.CreateUpdateSectionScoreSerializer(score, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)

    @decorators.action(detail=True, methods=['GET'], url_path='sections/(?P<section_pk>[^/.]+)')
    def section_detail(self, request, pk=None, section_pk=None):
        lesson_course = self.get_object()
        is_coach = getattr(request.user, "is_coach", False)

        if is_coach:
            section = Section.objects.filter(id=section_pk, course=lesson_course.course).only(
                "id", "title", "created_at", "cover_image"
            ).first()
            serializer = serializers.CourseSectionSerializer(section)
            return response.Response(serializer.data)

        else:
            allowed_section = get_objects_for_user(
                request.user,
                "can_access_section",
                klass=Section.objects.filter(id=section_pk, course=lesson_course.course).only(
                    "id", "title", "created_at", "cover_image"
                )
            ).first()
            if allowed_section is None:
                return response.Response({"detail": "You do not have access to this section."},
                                         status=status.HTTP_403_FORBIDDEN)
            serializer = serializers.CourseSectionSerializer(allowed_section)
            return response.Response(serializer.data)

    @decorators.action(detail=True, methods=['GET'], url_path="sections/(?P<section_pk>[^/.]+)/videos")
    def section_video(self, request, pk=None, section_pk=None):
        lesson_course = self.get_object()
        section_video = SectionVideo.objects.filter(section_id=section_pk, section__course=lesson_course.course).only(
            "id", "video", "created_at", "section__cover_image", "title"
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
            ).only("id", "video", "created_at", "section__cover_image", "title").first()
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
            "id", "zip_file", "created_at", "is_close", "title", "expired_data"
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
                "id", "zip_file", "created_at", "is_close", "title", "expired_data"
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


class LessonCoursePresentAbsent(viewsets.ModelViewSet):
    serializer_class = serializers.LessonCoursePreSentAbsentSerializer
    permission_classes = [IsCoachPermission]

    def get_queryset(self):
        return PresentAbsent.objects.filter(lesson_course_id=self.kwargs['lesson_course_pk']).defer(
            "is_deleted", "deleted_at", "created_at", "updated_at"
        )
