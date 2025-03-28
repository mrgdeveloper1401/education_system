from django.db.models import Prefetch, Q
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, viewsets, permissions, decorators, response, status, exceptions, views

from accounts.models import Student
from course.models import Comment, SectionVideo, SectionFile, LessonCourse, StudentSectionScore, \
    PresentAbsent, StudentAccessSection, SendSectionFile, OnlineLink, SectionQuestion, AnswerQuestion
from .pagination import CommentPagination
from .paginations import CourseCategoryPagination, CommonPagination

from . import serializers
from .permissions import IsCoachPermission


class PurchasesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.LessonCourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CourseCategoryPagination

    def get_serializer_class(self):
        if self.action == "send_file" and self.request.method == 'POST':
            return serializers.SendFileSerializer
        if self.action == "detail_send_file" and self.request.method in ['PUT', 'PATCH']:
            return serializers.SendFileSerializer
        if self.action == "poll_answer" and self.request.method == 'POST':
            return serializers.AnswerSectionQuestionSerializer
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
        query = LessonCourse.objects.filter(
            students__user=self.request.user, is_active=True).filter(
            Q(course__is_deleted=False) | Q(course__is_deleted=None)
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
        sections = StudentAccessSection.objects.filter(
            section__course__lesson_course__exact=pk,
            student__user=request.user,
            section__is_publish=True,
        ).only(
            "section__cover_image", "section__title", 'is_access'
        ).select_related("section").order_by("created_at")
        serializer = serializers.StudentAccessSectionSerializer(sections, many=True)
        return response.Response(serializer.data)

    @extend_schema(
        responses={200: serializers.StudentAccessSectionDetailSerializer}
    )
    @decorators.action(detail=True, methods=['GET'], url_path='sections/(?P<section_pk>[^/.]+)')
    def section_detail(self, request, pk=None, section_pk=None):
        section = (StudentAccessSection.objects.filter(
            section__course__lesson_course__exact=pk, student__user=request.user, section_id=section_pk,
            section__is_publish=True
        ).only('section__created_at', "section__cover_image", "section__title", "section__description", "is_access").
                   select_related("section").first())

        if not section:
            raise exceptions.NotFound()

        if section.is_access is False and request.user.student:
            raise exceptions.PermissionDenied("you do not view this section")

        serializer = serializers.StudentAccessSectionDetailSerializer(section)
        return response.Response(serializer.data)

    @extend_schema(responses={200: serializers.SectionQuestionSerializer})
    @decorators.action(detail=True, methods=['GET'], url_path="sections/(?P<section_pk>[^/.]+)/poll")
    def poll(self, request, pk=None, section_pk=None):
        section_question = SectionQuestion.objects.filter(
            section_id=section_pk,
            section__course__lesson_course__exact=pk
        ).only("question_title")
        serializer = serializers.SectionQuestionSerializer(section_question, many=True)
        return response.Response(serializer.data)

    @extend_schema(
        responses={200: serializers.CourseSectionFileSerializer},
        description="file_type --> main or more (mian = اصلی) (more = اضافی) (gold = طلایی)"
    )
    @decorators.action(detail=True, methods=['GET'], url_path='sections/(?P<section_pk>[^/.]+)/section_file')
    def section_file(self, request, pk=None, section_pk=None):
        section_file = SectionFile.objects.filter(
            section_id=section_pk,
            section__course__lesson_course__exact=pk,
            is_publish=True,
            section__is_publish=True
        ).only("zip_file", "title", "file_type")
        serializer = serializers.CourseSectionFileSerializer(section_file, many=True)
        return response.Response(serializer.data)

    @extend_schema(
        responses={200: serializers.CourseSectionFileSerializer},
        description="file_type --> main or more (mian = اصلی) (more = اضافی) (gold = طلایی)"
    )
    @decorators.action(
        detail=True,
        methods=['GET'],
        url_path="sections/(?P<section_pk>[^/.]+)/section_file/(?P<section_file_pk>[^/.]+)"
    )
    def detail_section_file(self, request, pk=None, section_pk=None, section_file_pk=None):
        section_file = SectionFile.objects.filter(
            section_id=section_pk,
            section__course__lesson_course__exact=pk,
            is_publish=True,
            section__is_publish=True,
            id=section_file_pk
        ).only("zip_file", "title", "file_type").first()

        if not section_file:
            raise exceptions.NotFound()

        serializer = serializers.CourseSectionFileSerializer(section_file)
        return response.Response(serializer.data)

    @extend_schema(
        responses={
            200: serializers.SendFileSerializer
        }
    )
    @decorators.action(
        detail=True,
        methods=['GET', 'POST'],
        url_path="sections/(?P<section_pk>[^/.]+)/section_file/(?P<section_file_pk>[^/.]+)/send_file"
    )
    def send_file(self, request, pk=None, section_pk=None, section_file_pk=None):
        ser = serializers.SendFileSerializer

        if request.method == 'GET':
            send_file = SendSectionFile.objects.filter(
                student__user=request.user,
                section_file_id=section_file_pk,
                section_file__section__course__lesson_course__exact=pk,
                section_file__section__is_publish=True,
                section_file__section_id=section_pk
            ).only("score", 'comment_student', "zip_file", "section_file", "created_at")
            serializer = ser(send_file, many=True)
            return response.Response(serializer.data)

        elif request.method == 'POST':
            serializer = ser(data=request.data, context={"section_file_pk": section_file_pk, "request": request})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            raise exceptions.MethodNotAllowed(request.method)

    @extend_schema(responses={200: serializers.SendFileSerializer})
    @decorators.action(
        detail=True,
        methods=['GET', "PUT", 'PATCH', 'DELETE'],
        url_path="sections/(?P<section_pk>[^/.]+)/section_file/(?P<section_file_pk>[^/.]+)/send_file/"
                 "(?P<send_file_pk>[^/.]+)"
    )
    def detail_send_file(self, request, pk=None, section_pk=None, section_file_pk=None, send_file_pk=None):
        send_file = SendSectionFile.objects.filter(
            id=send_file_pk,
            section_file_id=section_file_pk,
            section_file__section_id=section_pk,
            section_file__section__course__lesson_course__exact=pk,
            section_file__section__is_publish=True,
            section_file__section__student_section__is_access=True,
            student__user=request.user
        ).only("score", 'comment_student', "zip_file", "section_file").first()
        ser = serializers.SendFileSerializer
        ser.context = {"request": request, "section_file_pk": section_file_pk}

        if request.method == 'GET':
            serializer = ser(send_file)
            return response.Response(serializer.data)

        elif request.method == 'PUT':
            serializer = ser(send_file, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = ser(send_file, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data)

        elif request.method == 'DELETE':
            send_file.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise exceptions.MethodNotAllowed(request.method)

    @extend_schema(
        responses={
            200: serializers.CourseSectionVideoSerializer
        }
    )
    @decorators.action(detail=True, methods=['GET'], url_path="sections/(?P<section_pk>[^/.]+)/videos")
    def section_video(self, request, pk=None, section_pk=None):
        section_video = SectionVideo.objects.filter(
            section_id=section_pk,
            is_publish=True,
            section__is_publish=True,
            section__course__lesson_course__exact=pk
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
        score = StudentSectionScore.objects.filter(
            section_id=section_pk,
            section__course__lesson_course__exact=pk,
            student__user=request.user,
            section__is_publish=True,
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
            section_id=section_pk,
            student__user=request.user,
            section__is_publish=True,
            section__course__lesson_course__exact=pk
        ).only("student_status", "created_at")
        serializer = serializers.StudentPresentAbsentSerializer(present_absent, many=True)
        return response.Response(serializer.data)


class StudentPollAnswer(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.AnswerSectionQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]


class StudentLessonCourseViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsCoachPermission]
    serializer_class = serializers.StudentLessonCourseSerializer

    def get_queryset(self):
        return LessonCourse.objects.filter(coach__user=self.request.user).only(
            "students", "class_name"
        ).prefetch_related(
            Prefetch("students", Student.objects.filter(is_active=True).select_related("user").only(
                "student_number", "user__first_name", "user__last_name"
            ))
        )

    @extend_schema(
        tags=['api_coach_course']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class StudentListPresentAbsentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.StudentListPresentAbsentSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PresentAbsent.objects.filter(
            student__user=self.request.user,
            section__course__lesson_course__exact=self.kwargs["student_lesson_course_pk"],

        ).select_related("section").only("student_status", "section__title", "created_at")


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


class CoachLessonCourseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.LessonCourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = CommonPagination

    def get_serializer_class(self):
        if self.action == "coach_section_score" and self.request.method == 'POST':
            return serializers.CoachSectionScoreSerializer
        elif self.action == "detail_section_score" and self.request.method in ['PUT', 'PATCH']:
            return serializers.NestedCoachSectionScoreSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        query = LessonCourse.objects.filter(coach__user=self.request.user).select_related(
            "course", "coach__user"
        ).only(
            "course__course_name",
            "course__course_image",
            "course__project_counter",
            "progress",
            "coach__user__first_name",
            "coach__user__last_name",
            "class_name"
        )

        class_name = self.request.query_params.get("class_name")
        progress_lesson = self.request.query_params.get("progress_lesson")

        if class_name and progress_lesson:
            query = query.filter(class_name__icontains=class_name, progress__exact=progress_lesson)
        if class_name:
            query = query.filter(class_name__icontains=class_name)
        if progress_lesson:
            query = query.filter(progress__exact=progress_lesson)
        return query

    @extend_schema(
        tags=['api_coach_course'],
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
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=['api_coach_course']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        responses={
            200: serializers.CoachAccessSectionSerializer
        },
        tags=['api_coach_course']
    )
    @decorators.action(detail=True, methods=['GET'], url_path="sections")
    def get_coach_section(self, request, pk=None):
        sections = StudentAccessSection.objects.filter(
            section__course__lesson_course__exact=pk
        ).select_related("section").only('section__title', "section__cover_image", "is_access")
        serializer = serializers.CoachAccessSectionSerializer(sections, many=True)
        return response.Response(serializer.data)

    @extend_schema(
        responses={
            200: serializers.CoachAccessSectionSerializer
        },
        tags=['api_coach_course']
    )
    @decorators.action(detail=True, methods=['GET'], url_path="sections/(?P<section_pk>[^/.]+)")
    def detail_coach_section(self, request, pk=None, section_pk=None):
        section = StudentAccessSection.objects.filter(
            section__course__lesson_course__exact=pk, id=section_pk
        ).select_related("section").only('section__title', "section__cover_image", "is_access", "student_id").first()
        serializer = serializers.CoachAccessSectionSerializer(section)
        return response.Response(serializer.data)

    @extend_schema(
        responses={
            200: serializers.CourseSectionVideoSerializer
        },
        tags=['api_coach_course']
    )
    @decorators.action(detail=True, methods=['GET'], url_path="sections/(?P<section_pk>[^/.]+)/videos")
    def get_coach_video(self, request, pk=None, section_pk=None):
        access_section = StudentAccessSection.objects.select_related("section__course").only(
            "id", "section_id", "section__course_id",
        ).filter(id=section_pk).first()

        if not access_section:
            raise exceptions.NotFound()

        section_video = SectionVideo.objects.filter(
            section=access_section.section, is_publish=True, section__course__lesson_course__exact=pk
        ).select_related("section").only("video", "title", "section__cover_image")
        serializer = serializers.CourseSectionVideoSerializer(section_video, many=True)
        return response.Response(serializer.data)

    @extend_schema(
        responses={
            200: serializers.CourseSectionVideoSerializer
        },
        tags=['api_coach_course']
    )
    @decorators.action(
        detail=True,
        methods=['GET'],
        url_path="sections/(?P<section_pk>[^/.]+)/videos/(?P<video_pk>[^/.]+)")
    def detail_coach_video(self, request, pk=None, section_pk=None, video_pk=None):
        access_section = StudentAccessSection.objects.select_related("section__course").only(
            "id", "section_id", "section__course_id",
        ).get(id=section_pk)
        section_video = SectionVideo.objects.filter(
            section=access_section.section, is_publish=True, section__course=access_section.section.course,
            id=video_pk).select_related("section").only("video", "title", "section__cover_image").first()

        if not section_video:
            raise exceptions.NotFound()

        serializer = serializers.CourseSectionVideoSerializer(section_video)
        return response.Response(serializer.data)

    @extend_schema(
        tags=['api_coach_course'],
        parameters=[
            OpenApiParameter(
                name="file_type",
                description="searching the file type --> [main, more_then]",
                location=OpenApiParameter.QUERY,
                type=OpenApiTypes.STR,
            )
        ],
        responses={200: serializers.CoachStudentSendFileSerializer})
    @decorators.action(
        detail=True,
        methods=['GET', 'POST'],
        url_path="sections/(?P<section_pk>[^/.]+)/student_send_file")
    def coach_section_score(self, request, pk=None, section_pk=None):
        access_section = StudentAccessSection.objects.select_related("section__course").only(
            "id", "section_id", "section__course_id",
        ).filter(id=section_pk).first()

        if not access_section:
            raise exceptions.NotFound()

        section_score = SendSectionFile.objects.filter(
            section_file__section=access_section.section
        ).select_related("student__user", "section_file").only(
            "student__user__first_name",
            "student__user__last_name",
            "score",
            "comment_student",
            "comment_teacher",
            "created_at",
            "updated_at",
            "send_file_status",
            "zip_file",
            "section_file__file_type"
        )

        if request.method == "GET":

            file_type = request.query_params.get("file_type")

            if file_type:
                section_score = section_score.filter(section_file__file_type=file_type)

            serializer = serializers.CoachStudentSendFileSerializer(section_score, many=True)
            return response.Response(serializer.data)

        elif request.method == "POST":
            serializer = serializers.CoachSectionScoreSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)

        else:
            raise exceptions.MethodNotAllowed(request.method)

    @extend_schema(
        tags=['api_coach_course'],
        responses={
            200: serializers.NestedCoachSectionScoreSerializer
        }
    )
    @decorators.action(
        methods=['GET', 'PATCH', "PUT", 'DELETE'],
        detail=True,
        url_path="sections/(?P<section_pk>[^/.]+)/score/(?P<score_pk>[^/.]+)"
    )
    def detail_section_score(self, request, pk=None, section_pk=None, section_score=None, score_pk=None):
        access_section = StudentAccessSection.objects.select_related("section__course").only(
            "id", "section_id", "section__course_id",
        ).get(id=section_pk)
        section_score = StudentSectionScore.objects.filter(
            section=access_section.section
        ).select_related("student__user").only(
            "student__user__first_name", "student__user__last_name", 'score', "student_id"
        )
        ser = serializers.NestedCoachSectionScoreSerializer

        if request.method == "GET":
            serializer = ser(section_score, many=True)
            return response.Response(serializer.data)

        elif request.method == "PUT":
            if not section_score.exists():
                raise exceptions.NotFound("No score found for this section.")

            score_instance = section_score.first()
            serializer = ser(score_instance, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data)

        elif request.method == "PATCH":
            if not section_score.exists():
                raise exceptions.NotFound("No score found for this section.")

            score_instance = section_score.first()
            serializer = ser(score_instance, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data)

        elif request.method == "DELETE":
            if not section_score.exists():
                raise exceptions.NotFound("No score found for this section.")

            score_instance = section_score.first()
            score_instance.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)

        else:
            raise exceptions.MethodNotAllowed(request.method)

    @extend_schema(responses={200: serializers.CoachSectionFileSerializer}, tags=['api_coach_course'])
    @decorators.action(detail=True, methods=['GET'], url_path="sections/(?P<section_pk>[^/.]+)/section_file")
    def get_coach_section_file(self, request, pk=None, section_pk=None):
        section_file = SectionFile.objects.filter(
            section__student_section__exact=section_pk,
            section__course__lesson_course__exact=pk
        ).only(
            'zip_file', 'answer', "title", "file_type", "is_publish"
        )
        serializer = serializers.CoachSectionFileSerializer(section_file, many=True)
        return response.Response(serializer.data)

    @extend_schema(responses={200: serializers.CoachSectionFileSerializer}, tags=['api_coach_course'])
    @decorators.action(
        detail=True,
        methods=['GET'],
        url_path="sections/(?P<section_pk>[^/.]+)/section_file/(?P<section_file_pk>[^/.]+)")
    def detail_section_file(self, request, pk=None, section_pk=None, section_file_pk=None):
        section_file = SectionFile.objects.filter(
            id=section_file_pk, section__course__lesson_course__exact=pk
        ).only(
            'zip_file', 'answer', "title", "file_type", "is_publish"
        ).first()

        if not section_file:
            raise exceptions.NotFound()

        serializer = serializers.CoachSectionFileSerializer(section_file)
        return response.Response(serializer.data)


class OnlineLinkViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.OnlineLinkSerializer
    permission_classes = [IsCoachPermission]
    pagination_class = CommonPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['coach_lesson_course_pk'] = self.kwargs['coach_lesson_course_pk']
        return context

    def get_queryset(self):
        return OnlineLink.objects.filter(
            class_room__coach__user=self.request.user, class_room_id=self.kwargs['coach_lesson_course_pk']
        ).defer(
            "deleted_at", "is_deleted", "updated_at"
        )

    @extend_schema(
        tags=['api_coach_course']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=['api_coach_course']
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        tags=['api_coach_course']
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=['api_coach_course']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=['api_coach_course']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=['api_coach_course']
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class PresentAbsentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.CoachPresentAbsentSerializer
    permission_classes = [IsCoachPermission]
    pagination_class = CommonPagination
    queryset = PresentAbsent.objects.only("created_at", "student_status", "section_id", "student_id")

    @extend_schema(
        tags=['api_coach_course']
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @extend_schema(
        tags=['api_coach_course']
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @extend_schema(
        tags=['api_coach_course']
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        tags=['api_coach_course']
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        tags=['api_coach_course']
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        tags=['api_coach_course']
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class StudentOnlineLinkApiView(views.APIView):
    serializer_class = serializers.StudentOnlineLinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return OnlineLink.objects.filter(
            class_room_id=self.kwargs['student_lesson_course_pk'], is_publish=True
        ).only(
            "link", "created_at"
        ).last()

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.serializer_class(queryset)
        return response.Response(serializer.data)
