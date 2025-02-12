from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework import exceptions

from . import serializers
from course.models import Category, Course, Section
from .paginations import AdminPagination


class CategoryViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAdminUser]
    queryset = Category.objects.only("id", "category_name")
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
        return Course.objects.filter(category_id=self.kwargs["category_pk"]).only(
            "id", "course_image", "created_at", "course_name", "course_description", "course_description",
            "category_id", "course_price", "course_duration", "updated_at", "created_at"
        )

    def get_serializer_context(self):
        return {
            "category_pk": self.kwargs['category_pk']
        }

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
        if self.action == "list":
            return Section.objects.filter(course_id=self.kwargs["course_pk"]).only(
                "id", "section_image", "title"
            )
        return Section.objects.filter(course_id=self.kwargs["course_pk"])

    def get_serializer_context(self):
        return {
            "course_pk": self.kwargs["course_pk"],
        }

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.AdminListCourseSectionSerializer
        if self.action == "create":
            return serializers.AdminCreateCourseSectionSerializer
        if self.action in ['retrieve', "update", "partial_update", "destroy"]:
            return serializers.AdminUpdateCourseSectionSerializer
        else:
            raise exceptions.NotAcceptable()
