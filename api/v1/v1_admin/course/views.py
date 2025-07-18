from django.db.models import Prefetch
from rest_framework import viewsets, permissions, exceptions, generics, decorators, response, views, status, \
    mixins, filters
from drf_spectacular.views import extend_schema
from django_filters.rest_framework import DjangoFilterBackend

from accounts.models import Student
from . import serializers
from course.models import Category, Course, Section, SectionFile, SectionVideo, LessonCourse, Certificate, \
    PresentAbsent, SectionQuestion, AnswerQuestion, Comment, SignupCourse, StudentEnrollment
from .filters import AdminCommentFilter
from .paginations import AdminPagination
from ...course.filters import LessonCourseFilter
from ...course.paginations import CommonPagination


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAdminUser,)
    queryset = Category.objects.only("id", "category_name", "image", "description", "description_slug")
    pagination_class = CommonPagination

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.CreateCategorySerializer
        if self.action in ("list", "retrieve"):
            return serializers.ListRetrieveCategorySerializer
        if self.action in ('update', 'partial_update'):
            return serializers.UpdateCategoryNodeSerializer
        if self.action == "destroy":
            return serializers.ListRetrieveCategorySerializer
        else:
            raise exceptions.NotAcceptable


class AdminCourseViewSet(viewsets.ModelViewSet):
    """
    pagination --> 20 item
    filter query --> ?course_name=course_name
    """
    permission_classes = (permissions.IsAdminUser,)
    pagination_class = CommonPagination
    serializer_class = serializers.AdminCourseSerializer

    def get_queryset(self):
        return Course.objects.filter(category_id=self.kwargs["category_pk"]).defer("deleted_at", "is_deleted")

    def filter_queryset(self, queryset):
        course_name = self.request.query_params.get("course_name", None)
        query = queryset

        if course_name:
            query = queryset.filter(course_name__icontains=course_name)
        return query

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['category_pk'] = self.kwargs["category_pk"]
        return context


class AdminCourseSectionViewSet(viewsets.ModelViewSet):
    """
    filter query --> ?search=title \n
    ??is_last_section=true or false
    """
    permission_classes = (permissions.IsAdminUser,)
    pagination_class = CommonPagination
    serializer_class = serializers.AdminCreateCourseSectionSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ("is_last_section",)
    search_fields = ("title",)

    def get_queryset(self):
        return Section.objects.filter(course_id=self.kwargs["course_pk"]).defer("deleted_at", "is_deleted")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["course_pk"] = self.kwargs["course_pk"]
        return context


class AdminSectionFileViewSet(viewsets.ModelViewSet):
    """
    file_type --> main or more or gold
    zip_file --> (zip, rar)
    """
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = serializers.AdminCourseSectionFileSerializer

    def get_queryset(self):
        return SectionFile.objects.filter(section_id=self.kwargs["section_pk"]).only(
            "created_at",
            "updated_at",
            "zip_file",
            "section_id",
            "is_publish",
            "title",
            "answer",
            "created_at",
            "updated_at"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['section_pk'] = self.kwargs['section_pk']
        return context


class AdminSectionVideoViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = serializers.AdminSectionVideoSerializer

    def get_queryset(self):
        return SectionVideo.objects.filter(section_id=self.kwargs["section_pk"]).only(
            "created_at",
            "updated_at",
            "video",
            "video_url",
            "section_id",
            "is_publish",
            "title"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['section_pk'] = self.kwargs['section_pk']
        return context


# class AdminCourseListApiView(generics.ListAPIView):
#     """
#     filter query --> ?course_name=course_name
#     """
#     queryset = Course.objects.only("course_name",)
#     serializer_class = serializers.AdminCourseListSerializer
#     permission_classes = (permissions.IsAdminUser,)
#
#     def filter_queryset(self, queryset):
#         query = queryset
#         course_name = self.request.query_params.get("course_name", None)
#
#         if course_name:
#             query = query.filter(course_name__icontains=course_name)
#         return query


class AdminLessonCourseViewSet(viewsets.ModelViewSet):
    """
    filter query --> ?class_name=java \n
    ?class_name=python&progress=finished \n
    ?class_name=&progress=finished \n
    ?progress=not_started \n \n

    progress --> (not_started, finished, in_progress)
    """
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = serializers.AdminLessonCourseSerializer
    pagination_class = CommonPagination
    filterset_class = LessonCourseFilter

    def get_queryset(self):
        return LessonCourse.objects.filter(course_id=self.kwargs['course_pk']).prefetch_related(
            Prefetch("students", Student.objects.only("student_number"))
        ).defer(
            "is_deleted", "deleted_at"
        )

    @extend_schema(responses={200: serializers.AdminCoachRankingSerializer})
    @decorators.action(detail=True, methods=['GET'], url_path="student_poll_answer")
    def student_poll_answer(self, request, category_pk=None, course_pk=None, pk=None):
        answer_poll = AnswerQuestion.objects.filter(
            section_question__section__course_id=course_pk
        ).select_related("student__user", "section_question__section").only(
            "student__user__first_name",
            "student__user__last_name",
            "section_question__question_title",
            "rate",
            "section_question__section__title",
            "section_question"
        )
        serializer = serializers.AdminCoachRankingSerializer(answer_poll, many=True)
        return response.Response(serializer.data)


class AdminStudentPresentAbsentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.AdminStudentPresentAbsentSerializer
    permission_classes = (permissions.IsAdminUser,)
    pagination_class = AdminPagination
    filter_backends = (DjangoFilterBackend,)
    search_fields = ("student__user__first_name", "student__user__last_name")

    def get_queryset(self):
        return PresentAbsent.objects.only(
            "student_status",
            "student__user__first_name",
            "student__user__last_name",
            "section__title",
            "created_at"
        ).select_related("student__user", "section")


class AdminSectionQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AdminSectionQuestionSerializer
    permission_classes = (permissions.IsAdminUser,)

    def get_queryset(self):
        return SectionQuestion.objects.filter(section_id=self.kwargs['section_pk']).only(
            "question_title",
            "section",
            "is_publish",
            "created_at"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['section_pk'] = self.kwargs['section_pk']
        return context


class AdminAnswerQuestionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.AnswerQuestionSerializer
    permission_classes = (permissions.IsAdminUser,)

    def get_queryset(self):
        return AnswerQuestion.objects.filter(section_question_id=self.kwargs['section_question_pk']).only(
            "student",
            "section_question",
            "created_at",
            "rate"
        )


class AdminCommentViewSet(viewsets.ModelViewSet):
    """
    filter query --> ?is_pined=false or ?is_pined=true
    pagination --> 20 item
    permission --> admin user
    """
    serializer_class = serializers.AdminCommentSerializer
    pagination_class = AdminPagination
    permission_classes = (permissions.IsAdminUser,)
    filterset_class = AdminCommentFilter
    filter_backends = (DjangoFilterBackend,)

    def get_queryset(self):
        return Comment.objects.filter(
            category_id=self.kwargs['category_pk']
        ).only(
            "is_publish",
            "comment_body",
            "category",
            "path",
            "numchild",
            "depth",
            "user__first_name",
            "user__last_name",
            "created_at",
            "is_pined",
            "updated_at"
        ).select_related("user").order_by("-id")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['category_pk'] = self.kwargs['category_pk']
        return context

class SignUpCourseViewSet(viewsets.ModelViewSet):
    queryset = SignupCourse.objects.only(
            "course__course_name",
            "student_name",
            "phone_number",
            "created_at"
        )
    serializer_class = serializers.SignUpCourseSerializer

    def get_permissions(self):
        if self.request.method in ('PUT', 'PATCH', 'DELETE', "GET"):
            self.permission_classes = (permissions.IsAdminUser,)
        return super().get_permissions()


class AdminCertificateViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = serializers.AdminCertificateSerializer

    def get_queryset(self):
        return Certificate.objects.filter(section_id=self.kwargs['section_pk']).select_related(
            "student__user"
        ).only(
            "student__student_number",
            "student__user__first_name",
            "student__user__last_name",
            "unique_code",
            "qr_code",
            "final_pdf",
            "is_active",
            "created_at",
            "updated_at",
            "student__student_number"
        )


# class AdminCertificateStudentListView(mixins.ListModelMixin, viewsets.GenericViewSet):
#     """
#     filter query --> ?std_phone=student_phone_number
#     """
#     serializer_class = serializers.AdminStudentListCertificateSerializer
#     permission_classes = (permissions.IsAdminUser,)
#     queryset = Student.objects.select_related("user").only(
#         "user__mobile_phone",
#         "user__first_name",
#         "user__last_name"
#     )
#
#     def filter_queryset(self, queryset):
#         std_phone = self.request.query_params.get("std_phone", None)
#
#         if std_phone:
#             queryset = queryset.filter(user__mobile_phone__icontains=std_phone)
#         return queryset


class SyncStudentAccessSectionView(views.APIView):
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = serializers.SyncAdminCreateStudentSectionSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_201_CREATED)


class StudentEnrollmentView(viewsets.ModelViewSet):
    serializer_class = serializers.StudentEnrollmentSerializer
    permission_classes = (permissions.IsAdminUser,)

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.CreateStudentEnrollmentSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        return StudentEnrollment.objects.filter(
            lesson_course_id=self.kwargs['class_room_pk'],
        ).select_related("student").only(
            "student__student_number",
            "student_status"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['class_room_pk'] = self.kwargs['class_room_pk']
        return context
