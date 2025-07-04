from django.db.models import Prefetch
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter, extend_schema_view
from rest_framework import mixins, viewsets, permissions, decorators, response, status, exceptions, views, generics, \
    filters
from rest_framework.permissions import IsAuthenticated

from accounts.models import Student
from course.models import Comment, SectionVideo, SectionFile, LessonCourse, StudentSectionScore, \
    PresentAbsent, StudentAccessSection, SendSectionFile, OnlineLink, SectionQuestion, Section, \
    Category, CallLessonCourse, Course, Certificate, CourseTypeModel, StudentEnrollment
from .filters import LessonCourseFilter

from .pagination import CommentPagination
from .paginations import CommonPagination

from . import serializers
from .permissions import IsCoachPermission, IsAccessPermission, IsOwnerOrReadOnly


class PurchasesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    search query --> ?class_name=xyz or ?progress_lesson=xyz
    """
    serializer_class = serializers.LessonCourseSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CommonPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = LessonCourseFilter

    def get_serializer_class(self):
        if self.action == "send_file" and self.request.method == 'POST':
            return serializers.SendFileSerializer
        if self.action == "detail_send_file" and self.request.method in ('PUT', 'PATCH'):
            return serializers.SendFileSerializer
        if self.action == "poll_answer" and self.request.method == 'POST':
            return serializers.AnswerSectionQuestionSerializer
        if self.action == "section_certificate" and self.request.method == "POST":
            return serializers.CertificateSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        if self.action in (
            'section_detail',
            "poll",
            "section_file",
            "detail_section_file",
            "send_file",
            "detail_send_file",
            "section_video",
            "section_score",
            "section_score"
        ):
            self.permission_classes = (IsAuthenticated, IsAccessPermission)
        return super().get_permissions()


    def get_queryset(self):
        query = (LessonCourse.objects.filter(
           students__user=self.request.user,
            is_active=True,
        )
        ).select_related(
            "course__category", "coach__user"
        ).only(
            "course__course_name", "course__course_image", "course__project_counter", "coach__user__last_name",
            "coach__user__first_name", "progress", "class_name", "course__category__category_name"
        ).distinct()
        # std_enrollment = StudentEnrollment.objects.filter(student__user=self.request.user).only(
        #     "student_id"
        # ).distinct()
        # if std_enrollment:
        #     return query
        # return []
        return query

    # def filter_queryset(self, queryset):
    #     class_name = self.request.query_params.get("class_name") # for use search
    #     progress_lesson = self.request.query_params.get("progress_lesson") # for use search
    #
    #     if class_name and progress_lesson:
    #         queryset = queryset.filter(class_name__icontains=class_name, progress__exact=progress_lesson)
    #     elif class_name:
    #         queryset = queryset.filter(class_name__icontains=class_name)
    #     elif progress_lesson:
    #         queryset = queryset.filter(progress__exact=progress_lesson)
    #     return queryset

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
                # section_file__section__course__lesson_course__exact=pk,
                section_file__section__is_publish=True
                # section_file__section_id=section_pk
            ).only("score", 'comment_student', "zip_file", "section_file", "created_at", "comment_teacher",
                   "send_file_status", "updated_at")
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
            # section_file__section__course__lesson_course__exact=pk,
            section_file__section__is_publish=True,
            section_file__section__student_section__is_access=True,
            student__user=request.user
        ).only("score", 'comment_student', "zip_file", "section_file", "created_at", "comment_teacher",
               "send_file_status", "updated_at").first()
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

    @extend_schema(
        responses={
            201: serializers.CertificateSerializer
        }
    )
    @decorators.action(
        detail=True,
        url_path="sections/(?P<section_pk>[^/.]+)/certificate",
        methods=['GET', "POST"]
    )
    def section_certificate(self, request, pk=None, section_pk=None):
        if request.method == "POST":
            serializer = serializers.CertificateSerializer(
                data=request.data,
                context={"section_pk": section_pk, "request": request}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == "GET":
            queryset = Certificate.objects.filter(
                section_id=section_pk,
                section__course__lesson_course__exact=pk,
                student__user=request.user
            ).only(
                # "student__user__first_name",
                # "student__user__last_name",
                "section_id",
                # "created_at",
                "final_pdf"
            ).first()
            #.select_related(
            #     "student__user"
            # ).first()
            serializer = serializers.CertificateSerializer
            ser = serializer(queryset)
            return response.Response(ser.data)

        else:
            raise exceptions.MethodNotAllowed(request.method)


class StudentPollAnswer(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.AnswerSectionQuestionSerializer
    permission_classes = [permissions.IsAuthenticated]


@extend_schema_view(
    list=extend_schema(tags=['api_coach_course']),
    retrieve=extend_schema(tags=['api_coach_course']),
)
class StudentLessonCourseViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = (IsCoachPermission,)
    serializer_class = serializers.StudentLessonCourseSerializer

    def get_queryset(self):
        return StudentEnrollment.objects.filter(lesson_course_id=self.kwargs['coach_lesson_course_pk']).only(
            "student_status", "student__user__first_name", "student__user__last_name", "student__user__mobile_phone",
            "student__user__second_mobile_phone"
        ).select_related("student__user")


class StudentListPresentAbsentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.StudentListPresentAbsentSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return PresentAbsent.objects.filter(
            student__user=self.request.user,
            section__course__lesson_course__exact=self.kwargs["student_lesson_course_pk"],

        ).select_related("section").only("student_status", "section__title", "created_at")


class CommentViewSet(viewsets.ModelViewSet):
    """
    pagination --> 20 item
    permission --> is owner (everybody can delete, update own comment)
    """
    serializer_class = serializers.CommentSerializer
    permission_classes = (IsOwnerOrReadOnly,)
    pagination_class = CommentPagination

    def get_queryset(self):
        is_student = getattr(self.request.user, "is_student")
        query = Comment.objects.select_related("user").filter(is_publish=True).only(
            "comment_body", "user__first_name", "user__last_name", "created_at", "numchild", 'depth', "path",
            "numchild", "depth", "path", "user__image", "category_id", "user__is_coach"
        )

        is_pined = self.request.query_params.get("is_pined", None)

        if is_student and (is_pined and is_pined == 1):
            return query.filter(
                category__course_category__lesson_course=self.kwargs['student_lesson_course_pk'],
                is_pined=True
            )
        elif is_student:
            return query.filter(
                category__course_category__lesson_course=self.kwargs['student_lesson_course_pk']
            )
        elif is_pined and is_pined == 1:
            return query.filter(is_pined=True)
        else:
            return query.filter(
                category__course_category__lesson_course=self.kwargs['coach_lesson_course_pk']
            )


class CoachLessonCourseViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.ListCoachLessonCourseSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = CommonPagination

    def get_serializer_class(self):
        if self.action == "detail_student_send_files" and self.request.method in ('PUT', 'PATCH'):
            return serializers.UpdateCoachStudentSendFilesSerializer
        if self.action == "section_present_absent" and self.request.method in ('POST',):
            return serializers.CreateCoachPresentAbsentSerializer
        if self.action == "detail_coach_present_absent" and self.request.method in ('PUT', 'PATCH'):
            return serializers.CoachPresentAbsentSerializer
        # if self.action == "retrieve":
        #     return serializers.RetrieveLessonCourseSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        query = LessonCourse.objects.filter(coach__user=self.request.user).select_related(
            "course__category", "coach__user"
        ).only(
            "course__course_name",
            "course__course_image",
            "course__project_counter",
            "progress",
            "coach__user__first_name",
            "coach__user__last_name",
            "class_name",
            "course__category__category_name"
        )

        if "pk" in self.kwargs:
            query = query.prefetch_related(
                Prefetch("students",
                         queryset=Student.objects.select_related("user").only("user__first_name", "user__last_name"))
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

    @extend_schema(tags=['api_coach_course'])
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(responses={200: serializers.CoachSectionSerializer}, tags=['api_coach_course'])
    @decorators.action(detail=True, methods=['GET'], url_path="sections")
    def get_coach_section(self, request, pk=None):
        sections = Section.objects.filter(
            course__lesson_course__exact=pk
        ).only("title", "description", "cover_image")
        serializer = serializers.CoachSectionSerializer(sections, many=True)
        return response.Response(serializer.data)

    @extend_schema(
        tags=['api_coach_course'],
        responses={"201": serializers.CreateCoachPresentAbsentSerializer, 200: serializers.CoachPresentAbsentSerializer}
    )
    @decorators.action(
        detail=True,
        methods=['GET', 'POST'],
        url_path="sections/(?P<section_pk>[^/.]+)/present_absent")
    def section_present_absent(self, request, pk=None, section_pk=None):
        query = PresentAbsent.objects.filter(
            section_id=section_pk, section__course__lesson_course__exact=pk
        ).only(
            "student__user__first_name", "student__user__last_name", "section__title", "student_status", "created_at"
        )

        if request.method == 'GET':
            serializer = serializers.CoachPresentAbsentSerializer(query, many=True)
            return response.Response(serializer.data)
        else:
            serializer = serializers.CreateCoachPresentAbsentSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(tags=['api_coach_course'], responses={200: serializers.CoachPresentAbsentSerializer})
    @decorators.action(
        detail=True,
        methods=['GET', 'PUT', 'PATCH', "DELETE"],
        url_path="sections/(?P<section_pk>[^/.]+)/present_absent/(?P<present_absent_pk>[^/.]+)"
    )
    def detail_coach_present_absent(self, request, pk=None, section_pk=None, present_absent_pk=None):
        query = PresentAbsent.objects.filter(
            id=present_absent_pk, section_id=section_pk, section__course__lesson_course__exact=pk
        ).select_related("student__user", "section").only(
            "student__user__first_name", "student__user__last_name", "section__title", "student_status", "created_at"
        ).first()

        if not query:
            raise exceptions.NotFound()

        ser = serializers.CoachPresentAbsentSerializer

        if request.method == 'GET':
            serializer = ser(query)
            return response.Response(serializer.data)

        elif request.method == 'PUT':
            serializer = ser(query, request.data, context={'section_pk': section_pk})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = ser(query, request.data, partial=True, context={"section_pk": section_pk})
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data)

        else:
            query.delete()
            return response.Response(status=status.HTTP_204_NO_CONTENT)

    @extend_schema(responses={200: serializers.CourseSectionVideoSerializer}, tags=['api_coach_course'])
    @decorators.action(detail=True, methods=['GET'], url_path="sections/(?P<section_pk>[^/.]+)/videos")
    def get_coach_video(self, request, pk=None, section_pk=None):
        section_video = SectionVideo.objects.filter(
            section_id=section_pk, section__course__lesson_course__exact=pk
        ).select_related("section").only("video", "title", "section__cover_image")
        serializer = serializers.CourseSectionVideoSerializer(section_video, many=True)
        return response.Response(serializer.data)

    @extend_schema(
        tags=['api_coach_course'],
        responses={
            200: serializers.CoachSendFileSerializer
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
        ser = serializers.CoachSendFileSerializer

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
            section_id=section_pk,
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

    @extend_schema(responses={200: serializers.CoachStudentSendFilesSerializer}, tags=['api_coach_course'],
                   parameters=[
                       OpenApiParameter(
                           name="file_type",
                           description="searching the file type --> [main, more_then]",
                           location=OpenApiParameter.QUERY,
                           type=OpenApiTypes.STR,
                       ),
                       OpenApiParameter(
                           name='file_status',
                           description="searching into filed send_file_status --> [sending, accept_to_wait, accepted]",
                           location=OpenApiParameter.QUERY,
                           type=OpenApiTypes.STR,
                       )
                   ]

                   )
    @decorators.action(
        detail=True,
        methods=['GET'],
        url_path="sections/(?P<section_pk>[^/.]+)/student_send_files"
    )
    def student_send_files(self, request, pk=None, section_pk=None):
        query = SendSectionFile.objects.filter(
            section_file__section_id=section_pk,
            section_file__section__course__lesson_course__exact=pk
        ).select_related("student__user", "section_file").only(
            "student_id", "student__user__first_name", "student__user__last_name", "zip_file", "comment_student",
            "comment_teacher", "section_file__file_type", "created_at", "updated_at", "send_file_status", "score"
        )

        file_type = request.query_params.get("file_type")
        file_status = request.query_params.get("file_status")

        if file_type and file_status:
            query = query.filter(section_file__file_type=file_type, send_file_status__exact=file_status)
        elif file_status:
            query = query.filter(send_file_status__exact=file_status)
        elif file_type:
            query = query.filter(section_file__file_type=file_type)
        else:
            query = query

        serializer = serializers.CoachStudentSendFilesSerializer(query, many=True)
        return response.Response(serializer.data)

    @extend_schema(responses={200: serializers.CoachStudentSendFilesSerializer}, tags=['api_coach_course'])
    @decorators.action(
        detail=True,
        methods=['GET', "PUT", "PATCH"],
        url_path="sections/(?P<section_pk>[^/.]+)/student_send_files/(?P<student_send_files_pk>[^/.]+)"
    )
    def detail_student_send_files(self, request, pk=None, section_pk=None, student_send_files_pk=None):
        query = SendSectionFile.objects.filter(
            id=student_send_files_pk,
            section_file__section_id=section_pk,
            section_file__section__course__lesson_course__exact=pk
        ).only(
            "student__user__first_name", "student__user__last_name", "zip_file", "comment_student", "comment_teacher",
            "score", "created_at", "updated_at", "section_file__file_type", "send_file_status"
        ).select_related("student__user", "section_file").first()

        if not query:
            raise exceptions.NotFound()

        if request.method == "GET":
            serializer = serializers.CoachStudentSendFilesSerializer(query)
            return response.Response(serializer.data)

        elif request.method == 'PUT':
            serializer = serializers.UpdateCoachStudentSendFilesSerializer(query, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data)

        elif request.method == 'PATCH':
            serializer = serializers.UpdateCoachStudentSendFilesSerializer(query, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return response.Response(serializer.data)

        else:
            raise exceptions.MethodNotAllowed(request.method)


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


@extend_schema(
    tags=['api_coach_course'], description="status --> [successful, un_successful]"
)
class CallLessonCourseViewSet(viewsets.ModelViewSet):
    """
    search student --> ?std_id=student_number
    """
    serializer_class = serializers.CallLessonCourseSerializer
    permission_classes = (IsCoachPermission,)
    pagination_class = CommonPagination

    def get_queryset(self):
        return CallLessonCourse.objects.filter(
            lesson_course_id=self.kwargs['coach_lesson_course_pk'], lesson_course__is_active=True
        ).only(
            "cancellation_alert", "call", "call_answering", "project", "call_date", "result_call",
            "lesson_course__class_name", "created_at", "updated_at", "status"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["lesson_course_pk"] = self.kwargs['coach_lesson_course_pk']
        return context

    def filter_queryset(self, queryset):
        std = self.request.query_params.get("std_id", None)

        if std:
            return queryset.filter(student__id=std)
        else:
            return queryset


class HomeCategoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    queryset = Category.objects.only(
        "category_name",
        "image",
        "description",
        "description_slug"
    )
    serializer_class = serializers.HomeCategorySerializer


class HomeCourseViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    course_type is (basic, indeterminate, advanced), \n
    for search filed you can use in url
    ?course_type=basic or ?course_type=indeterminate or ?course_type=advanced
    """
    serializer_class = serializers.HomeCourseSerializer

    def get_queryset(self):
        query = Course.objects.filter(category_id=self.kwargs['home_category_pk']).defer(
            "is_deleted", "deleted_at", "updated_at", "created_at"
        ).prefetch_related(
            Prefetch("course_type_model", queryset=CourseTypeModel.objects.filter(is_active=True).only(
                "price", "course_type", "description", "course_id", "plan_type", "amount"
            ))
        ).order_by("id")
        course_level = self.request.query_params.get("course_level", None)

        if course_level:
            query = query.filter(course_level__exact=course_level)

        return query


class CrudCourseTypeViewSet(viewsets.ModelViewSet):
    """
    plan typ can be set this --> month - year - day
    """
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = serializers.CrudCourseTypeSerializer

    def get_queryset(self):
        return CourseTypeModel.objects.filter(
            course_id=self.kwargs['course_pk']
        ).only(
            "course__course_name",
            "created_at",
            "updated_at",
            "is_active",
            "price",
            "description",
            "course_type",
            "plan_type",
            "is_active",
            "amount"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['course_pk'] = self.kwargs['course_pk']
        return context


class AllCourseViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    pagination --> 20 item
    search --> ?name=course_name
    """
    serializer_class = serializers.AllCourseSerializer
    pagination_class = CommentPagination
    queryset = Course.objects.filter(is_publish=True).only(
        "course_name",
        "course_description",
        "course_image",
        "project_counter",
        "facilities",
        "course_level",
        "time_course",
        "course_age",
        "description_slug"
    )

    def filter_queryset(self, queryset):
        name = self.request.query_params.get("name", None)

        if name:
            return queryset.filter(course_name=name)
        return queryset


class SendNotificationUserSendSectionFileView(generics.CreateAPIView):
    queryset = None
    serializer_class = serializers.SendNotificationUserSendSectionFile
    permission_classes = (permissions.IsAuthenticated,)


class ListCourseIdTitleView(generics.ListAPIView):
    """
    list course contain --> id, title \n
    search --> ?search=test
    """
    queryset = Course.objects.filter(is_publish=True).only(
        "course_name"
    )
    serializer_class = serializers.ListCourseIdTitleSerializer
    search_fields = ("course_name__icontains",)
    filter_backends = (filters.SearchFilter,)
    # permission_classes = (permissions.IsAdminUser,)
