from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet, GenericViewSet
from rest_framework import permissions
from rest_framework import mixins
from rest_framework.exceptions import NotAcceptable, ValidationError
from django.utils.translation import gettext_lazy as _

from course.models import Category, Course, Comment, Section, SectionImage
from .pagination import CommentPagination
from .paginations import CourseCategoryPagination
from .permissions import AccessCoursePermission, AccessCourseSectionPermission, AccessCourseSectionImagePermission
from .serializers import CourseSerializer, CreateCategorySerializer, CategoryNodeSerializer, \
    UpdateCategoryNodeSerializer, DestroyCategoryNodeSerializer, CommentSerializer, SectionSerializer, \
    ListSectionSerializer, CreateSectionSerializer, SectionImageSerializer, ListSectionImageSerializer, \
    RetrieveSectionImageSerializer


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.all()
    pagination_class = CourseCategoryPagination

    # def get_permissions(self):
    #     if self.request.method not in permissions.SAFE_METHODS:
    #         return [permissions.IsAdminUser()]
    #     return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return CreateCategorySerializer
        if self.action == "list":
            return CategoryNodeSerializer
        if self.action == "retrieve":
            return CategoryNodeSerializer
        if self.action == 'update':
            return UpdateCategoryNodeSerializer
        if self.action == "partial_update":
            return UpdateCategoryNodeSerializer
        if self.action == "destroy":
            return DestroyCategoryNodeSerializer
        else:
            raise NotAcceptable()

    # def perform_destroy(self, instance):
    #     if instance.numchild >= 1 or instance.course_category.count() > 0:
    #         raise ValidationError({'detail': _("this data have child node")})
    #     instance.delete()


class CourseViewSet(ReadOnlyModelViewSet):
    serializer_class = CourseSerializer
    permission_classes = [AccessCoursePermission]
    pagination_class = CourseCategoryPagination

    # def get_permissions(self):
    #     if self.request.method not in permissions.SAFE_METHODS:
    #         return [permissions.IsAdminUser()]
    #     return super().get_permissions()

    def get_queryset(self):
        return Course.objects.filter(category_id=self.kwargs["category_pk"]).select_related("category")

    def get_serializer_context(self):
        if "category_pk" in self.kwargs:
            return {'category_pk': self.kwargs["category_pk"]}
        return super().get_serializer_context()


class SectionViewSet(ReadOnlyModelViewSet):
    serializer_class = SectionSerializer
    permission_classes = [AccessCourseSectionPermission]

    # def get_permissions(self):
    #     if self.request.method not in permissions.SAFE_METHODS:
    #         return [permissions.IsAdminUser()]
    #     return [IsAuthenticated()]

    def get_queryset(self):
        if self.action == "list":
            section = Section.objects.only("id", "title").filter(is_available=True)
        else:
            section = Section.objects.filter(course_id=self.kwargs['course_pk'], is_available=True)
        return section

    def get_serializer_context(self):
        return {"course_pk": self.kwargs["course_pk"]}

    def get_serializer_class(self):
        if self.action == "list":
            return ListSectionSerializer
        if self.action == "create":
            return CreateSectionSerializer
        return super().get_serializer_class()


class ListRetrieveSectionImageViewSet(ReadOnlyModelViewSet):
    queryset = SectionImage.objects.filter(is_active=True).select_related("image")
    permission_classes = [AccessCourseSectionImagePermission]

    def get_serializer_class(self):
        if self.action == "list":
            return ListSectionImageSerializer
        if self.action == 'retrieve':
            return RetrieveSectionImageSerializer
        else:
            raise NotAcceptable

# class LessonByStudentTakenViewSet(ReadOnlyModelViewSet):
#     # queryset = LessonTakenByStudent.objects.select_related("course", "student")
#     serializer_class = LessonByTakenStudentSerializer
#     permission_classes = [StudentPermission]
#     pagination_class = LessonTakenPagination
#
#     def get_queryset(self):
#         student = get_object_or_404(Student, user=self.request.user)
#         return LessonTakenByStudent.objects.filter(student=student).select_related("student__user", "course")
#
#
# class LessonByCoachTakenViewSet(ReadOnlyModelViewSet):
#     serializer_class = LessonTakenByCoachSerializer
#     permission_classes = [CoachPermission]
#     pagination_class = LessonTakenPagination
#
#     def get_queryset(self):
#         coach = get_object_or_404(Coach, user=self.request.user)
#         return LessonTakenByCoach.objects.filter(coach=coach).select_related("coach__user", "course")
#
#
# class ScoreViewSet(ModelViewSet):
#     serializer_class = ScoreSerializer
#     queryset = Score.objects.all()
#     permission_classes = [EditScorePermission]
#
#     def get_serializer_context(self):
#         return {"user": self.request.user}


class CommentViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CommentPagination

    def get_queryset(self):
        return Comment.objects.filter(course_id=self.kwargs['course_pk'])

    def get_serializer_context(self):
        return {
            "user": self.request.user,
            "course_pk": self.kwargs["course_pk"]
        }


# class PracticeViewSet(ModelViewSet):
#     serializer_class = PracticeSerializer
#     permission_classes = [PracticePermission]
#
#     def get_queryset(self):
#         course = get_object_or_404(Course, pk=self.kwargs["course_pk"])
#         return Practice.objects.filter(course=course).select_related('coach__user', "course")
#
#     def get_serializer_context(self):
#         return {
#             "user": self.request.user,
#             "course_pk": self.kwargs['course_pk']
#         }
#
#
# class SubmitPracticeViewSet(ModelViewSet):
#     serializer_class = PracticeSubmitSerializer
#     permission_classes = [SubmitPracticePermissions]
#
#     def get_queryset(self):
#         course = get_object_or_404(Course, pk=self.kwargs['course_pk'])
#         practice = get_object_or_404(Practice, course=course, pk=self.kwargs['practice_pk'])
#         return PracticeSubmission.objects.filter(practice=practice, student__user=self.request.user).select_related(
#             "student__user", "practice"
#         )
#
#     def get_serializer_context(self):
#         return {
#             "user": self.request.user,
#             "practice_pk": self.kwargs['practice_pk'],
#             "course_pk": self.kwargs['course_pk']
#         }
#
#
# class QuizViewSet(ModelViewSet):
#     serializer_class = QuizSerializer
#     permission_classes = [QuizPermission]
#
#     def get_queryset(self):
#         term = get_object_or_404(Term, pk=self.kwargs['term_pk'])
#         course = get_object_or_404(Course, term=term, pk=self.kwargs['course_pk'])
#         return Quiz.objects.filter(course=course).select_related('course', "coach__user")
#
#     def get_serializer_context(self):
#         return {
#             "user": self.request.user,
#             "course_pk": self.kwargs['course_pk'],
#         }
#
#
# class QuestionViewSet(ModelViewSet):
#     serializer_class = QuestionSerializer
#     permission_classes = [QuestionPermission]
#
#     def get_queryset(self):
#         return Question.objects.filter(quiz_id=self.kwargs["quiz_pk"]).select_related("quiz__coach__user")
#
#     def get_serializer_context(self):
#         return {
#             "quiz_pk": self.kwargs['quiz_pk']
#         }
#
#
# class ClassRoomViewSet(ModelViewSet):
#     queryset = ClassRoom.objects.prefetch_related("student__user", "coach__user").select_related("course")
#     serializer_class = ClassRoomSerializer
#
#     def get_serializer_context(self):
#         return {
#             "course_pk": self.kwargs['course_pk']
#         }
