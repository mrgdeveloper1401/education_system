from django.db.models import Prefetch
from rest_framework import mixins, viewsets, permissions, generics
from rest_framework.exceptions import NotAcceptable

from course.models import Category, Course, Comment, Section, SectionVideo, SectionFile, SendSectionFile, LessonCourse, \
    StudentAccessCourse, CoachAccessCourse
from .pagination import CommentPagination
from .paginations import CourseCategoryPagination, LessonTakenPagination

from . import serializers
from .permissions import StudentAccessCoursePermission, StudentAccessCourseSectionPermission, \
    StudentAccessCourseSectionFilePermission, StudentAccessCourseSendSectionFilePermission, IsCoachAuthenticated


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Category.objects.only("id", "category_name")
    pagination_class = CourseCategoryPagination

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.CategoryNodeSerializer
        if self.action == "retrieve":
            return serializers.CategoryNodeSerializer
        else:
            raise NotAcceptable()


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    pagination_class = CourseCategoryPagination
    permission_classes = [StudentAccessCoursePermission]

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


class SectionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [StudentAccessCourseSectionPermission]

    def get_queryset(self):
        if self.action == "list":
            return Section.objects.filter(course_id=self.kwargs['course_pk'], is_available=True).only(
                "id", "course", "title", "created_at", "cover_image"
            )
        else:
            return (Section.objects.filter(course_id=self.kwargs['course_pk'], is_available=True).only(
                "course_id", "title", "description", "cover_image"
            ))

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.ListSectionSerializer
        else:
            return serializers.RetrieveSectionSerializer


class SectionVideoViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [StudentAccessCourseSectionFilePermission]

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


class SectionFileViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [StudentAccessCourseSectionFilePermission]

    def get_queryset(self):
        query = SectionFile.objects.filter(is_publish=True, section_id=self.kwargs["section_pk"])
        if self.action == "list":
            q = query.only("id", "zip_file", "created_at", "title", "is_close")
        else:
            q = query.only("zip_file", "expired_data")
        return q

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.ListSectionFileSerializer
        else:
            return serializers.RetrieveSectionFileSerializer


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


class SendSectionFileViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.SendSectionFileSerializer
    permission_classes = [StudentAccessCourseSendSectionFilePermission]
    
    def get_queryset(self):
        return SendSectionFile.objects.filter(section_file_id=self.kwargs['section_file_pk'],
                                              student__user=self.request.user).defer(
            'is_deleted', "deleted_at"
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['section_file_pk'] = self.kwargs['section_file_pk']
        context['section_pk'] = self.kwargs['section_pk']
        return context


class CoachTakenCourseApiView(generics.ListAPIView):
    serializer_class = serializers.LessonTakenByCoachSerializer
    permission_classes = [IsCoachAuthenticated]

    def get_queryset(self):
        query = LessonCourse.objects.filter(coach__user=self.request.user, is_active=True).select_related(
            "course", "coach__user"
        ).only(
            "course__course_image", "coach__user__first_name", "coach__user__last_name", "class_name", "created_at",
            "progress"
        ).prefetch_related(
            Prefetch("course__sections", queryset=Section.objects.only("title", "course_id")),
            Prefetch("course__sections__section_videos", queryset=SectionVideo.objects.only("video", "section_id")),
            Prefetch("course__sections__section_files", queryset=SectionFile.objects.only("zip_file", "section_id"))
        )
        progress_bar = self.request.query_params.get("progress")
        if progress_bar:
            q = query.filter(progress=progress_bar)
        else:
            q = query
        return q


class StudentTakenCourseApiView(generics.ListAPIView):
    serializer_class = serializers.LessonTakenByStudentSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = LessonTakenPagination

    def get_queryset(self):
        query = LessonCourse.objects.filter(students__user=self.request.user, is_active=True).only(
            "coach", "course", "progress"
        )
        progress_bar = self.request.query_params.get("progress")
        if progress_bar:
            q = query.filter(progress=progress_bar)
        else:
            q = query
        return q
