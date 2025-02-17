from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework import mixins
from rest_framework.exceptions import NotAcceptable

from course.models import Category, Course, Comment, Section, SectionVideo, SectionFile
from .pagination import CommentPagination
from .paginations import CourseCategoryPagination
from .permissions import AccessCoursePermission, AccessCourseSectionPermission, AccessCourseSectionImagePermission
from . import serializers


class CategoryViewSet(ReadOnlyModelViewSet):
    queryset = Category.objects.only("id", "category_name")
    pagination_class = CourseCategoryPagination

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.CategoryNodeSerializer
        if self.action == "retrieve":
            return serializers.CategoryNodeSerializer
        else:
            raise NotAcceptable()


class CourseViewSet(ReadOnlyModelViewSet):
    permission_classes = [AccessCoursePermission]
    pagination_class = CourseCategoryPagination

    def get_queryset(self):
        query = Course.objects.filter(category_id=self.kwargs["category_pk"], is_publish=True)
        if self.action == "list":
            return query.only(
                "id", "course_name", "course_image", "course_price", "course_duration"
            )
        else:
            return query.only(
                "id", "course_name", "course_image", "course_price", "course_duration", "course_description"
            )

    def get_serializer_context(self):
        if "category_pk" in self.kwargs:
            return {'category_pk': self.kwargs["category_pk"]}
        return super().get_serializer_context()

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.ListCourseSerializer
        else:
            return serializers.RetrieveCourseSerializer


class SectionViewSet(ReadOnlyModelViewSet):
    permission_classes = [AccessCourseSectionPermission]

    def get_queryset(self):
        if self.action == "list":
            return Section.objects.filter(course_id=self.kwargs['course_pk'], is_available=True).only(
                "id", "course", "title", "created_at", "cover_image"
            )
        else:
            return (Section.objects.filter(course_id=self.kwargs['course_pk'], is_available=True).select_related(
                "course"
            ).only(
                "course_id", "title", "description", "cover_image"
            ))

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.ListSectionSerializer
        else:
            return serializers.RetrieveSectionSerializer


class SectionVideoViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.ListSectionVideoSerializer
        else:
            return serializers.RetrieveSectionVideoSerializer

    def get_queryset(self):
        query = SectionVideo.objects.filter(is_publish=True, section_id=self.kwargs["section_pk"])
        if self.action == "list":
            query = query.only("id", "created_at", "video")
        else:
            query = query.only("video")
        return query


class SectionFileViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = SectionFile.objects.filter(is_publish=True, section_id=self.kwargs["section_pk"])
        if self.action == "list":
            q = query.only("id", "pdf_file", "created_at")
        else:
            q = query.only("pdf_file")
        return q

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.ListSectionFileSerializer
        else:
            return serializers.RetrieveSectionFileSerializer


class CommentViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.RetrieveModelMixin, GenericViewSet):
    serializer_class = serializers.CommentSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CommentPagination

    def get_queryset(self):
        return Comment.objects.filter(course_id=self.kwargs['course_pk'])

    def get_serializer_context(self):
        return {
            "user": self.request.user,
            "course_pk": self.kwargs["course_pk"]
        }
