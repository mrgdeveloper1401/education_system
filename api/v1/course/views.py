from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework import mixins
from rest_framework.exceptions import NotAcceptable

from course.models import Category, Course, Comment, Section
from .pagination import CommentPagination
from .paginations import CourseCategoryPagination
from .permissions import AccessCoursePermission, AccessCourseSectionPermission, AccessCourseSectionImagePermission
from .serializers import CourseSerializer, CategoryNodeSerializer, \
    CommentSerializer, SectionSerializer, \
    ListSectionSerializer, CreateSectionSerializer, ListCourseSerializer, RetrieveCourseSerializer


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.only("id", "category_name")
    pagination_class = CourseCategoryPagination

    def get_serializer_class(self):
        if self.action == "list":
            return CategoryNodeSerializer
        if self.action == "retrieve":
            return CategoryNodeSerializer
        else:
            raise NotAcceptable()


class CourseViewSet(ReadOnlyModelViewSet):
    # serializer_class = CourseSerializer
    permission_classes = [AccessCoursePermission]
    pagination_class = CourseCategoryPagination

    def get_queryset(self):
        if self.action == "list":
            return (Course.objects.filter(category_id=self.kwargs["category_pk"]).select_related("course_image").
                    only("id", "course_name", "course_price", "course_duration", "course_image"))
        else:
            return Course.objects.filter(category_id=self.kwargs["category_pk"])

    def get_serializer_context(self):
        if "category_pk" in self.kwargs:
            return {'category_pk': self.kwargs["category_pk"]}
        return super().get_serializer_context()

    def get_serializer_class(self):
        if self.action == "list":
            return ListCourseSerializer
        else:
            return RetrieveCourseSerializer


class SectionViewSet(ReadOnlyModelViewSet):
    serializer_class = SectionSerializer
    permission_classes = [AccessCourseSectionPermission]

    def get_queryset(self):
        if self.action == "list":
            section = Section.objects.only("id", "title").filter(course_id=self.kwargs['course_pk'], is_available=True)
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


# class ListRetrieveSectionImageViewSet(ReadOnlyModelViewSet):
#     permission_classes = [AccessCourseSectionImagePermission]
#
#     def get_serializer_class(self):
#         if self.action == "list":
#             return ListSectionImageSerializer
#         if self.action == 'retrieve':
#             return RetrieveSectionImageSerializer
#         else:
#             raise NotAcceptable
#
#     def get_queryset(self):
#         if self.action == "list":
#             return SectionImage.objects.filter(is_active=True, section_id=self.kwargs['section_pk']).only("id", "image")
#         if self.action == "retrieve":
#             return (SectionImage.objects.filter(is_active=True, section_id=self.kwargs['section_pk']).
#                     select_related("section__course"))


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
