from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import  OpenApiParameter
from rest_framework import viewsets, permissions, exceptions, generics, filters, decorators, response, views, status
from drf_spectacular.views import extend_schema

from utils.permissions import NotAuthenticate
from . import serializers
from course.models import Category, Course, Section, SectionFile, SectionVideo, LessonCourse, Certificate, \
    PresentAbsent, Question, SectionQuestion, AnswerQuestion, Comment, SignupCourse
from .paginations import AdminPagination


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = Category.objects.only("id", "category_name", "image", "description")
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
    """
    file_type --> main or more or gold
    """
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.AdminCreateCourseSectionFileSerializer
        else:
            return serializers.AdminListCourseSectionFileSerializer

    def get_queryset(self):
        return SectionFile.objects.filter(section_id=self.kwargs["section_pk"]).only(
            "id", "created_at", "updated_at", "zip_file", "section_id", "is_publish", "title", "answer"
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

    @extend_schema(responses={200: serializers.AdminCoachRankingSerializer})
    @decorators.action(detail=True, methods=['GET'], url_path="student_poll_answer")
    def student_poll_answer(self, request, category_pk=None, course_pk=None, pk=None):
        answer_poll = AnswerQuestion.objects.filter(
            section_question__section__course_id=course_pk
        ).select_related("student__user", "section_question__section").only(
            "student__user__first_name", "student__user__last_name", "section_question__question_title", "rate",
            "section_question__section__title", "section_question"
        )
        serializer = serializers.AdminCoachRankingSerializer(answer_poll, many=True)
        return response.Response(serializer.data)


class AdminCertificateViewSet(viewsets.ModelViewSet):
    queryset = Certificate.objects.defer("deleted_at", "is_deleted", "created_at", "updated_at")
    serializer_class = serializers.AdminCertificateSerializer
    permission_classes = [permissions.IsAdminUser]


class AdminStudentPresentAbsentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.AdminStudentPresentAbsentSerializer
    permission_classes = [permissions.IsAdminUser]
    pagination_class = AdminPagination

    def get_queryset(self):
        query = PresentAbsent.objects.only(
            "student_status", "student__user__first_name", "student__user__last_name", "section__title", "created_at"
        ).select_related("student__user", "section")
        first_name = self.request.query_params.get('first_name')
        last_name = self.request.query_params.get('last_name')

        if first_name:
            query = query.filter(student__user__first_name__icontains=first_name)
        elif last_name:
            query = query.filter(student__user__last_name__icontains=last_name)
        elif first_name and last_name:
            query = query.filter(
                student__user__last_name__icontains=first_name, student__user__first_name__icontains=last_name
            )
        else:
            query = query
        return query


class AdminSectionQuestionViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AdminSectionQuestionSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return SectionQuestion.objects.filter(section_id=self.kwargs['section_pk']).only(
            "question_title", "section", "is_publish", "created_at"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['section_pk'] = self.kwargs['section_pk']
        return context


class AdminAnswerQuestionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = serializers.AnswerQuestionSerializer
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return AnswerQuestion.objects.filter(section_question_id=self.kwargs['section_question_pk']).only(
            "student", "section_question", "created_at", "rate"
        )


class AdminCommentViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AdminCommentSerializer
    pagination_class = AdminPagination
    permission_classes = [permissions.IsAdminUser]

    def get_queryset(self):
        return Comment.objects.filter(
            category_id=self.kwargs['category_pk']
        ).only(
            "is_publish", "comment_body", "category", "path", "numchild", "depth", "user__first_name", "user__last_name",
            "created_at"
        ).select_related("user")

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
        if self.request.method in ['PUT', 'PATCH', 'DELETE', "GET"]:
            self.permission_classes = (permissions.IsAdminUser,)
        return super().get_permissions()


class ResentOtpCodeView(views.APIView):
    """
    this view you can use resent otp code,
    when user create SingUpCourse
    """
    permission_classes = (NotAuthenticate,)
    serializer_class = serializers.ResentOtpCodeSerializer

    @extend_schema(
        tags=("api_admin_course",)
    )
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(serializer.data, status=status.HTTP_201_CREATED)
