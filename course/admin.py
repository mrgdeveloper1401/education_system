from django.contrib import admin
from treebeard.forms import movenodeform_factory
from treebeard.admin import TreeAdmin
from import_export.admin import ImportExportModelAdmin

from . import models


@admin.register(models.Course)
class CouAdmin(ImportExportModelAdmin):
    list_display = ["category", "course_name", "course_price", "course_duration", "is_publish"]
    list_filter = ['created_at']
    raw_id_fields = ['category']
    list_select_related = ['category']
    search_fields = ['course_name']


@admin.register(models.Category)
class CategoryTreeAdmin(TreeAdmin, ImportExportModelAdmin):
    form = movenodeform_factory(models.Category)
    list_per_page = 20


@admin.register(models.Section)
class SectionAdmin(admin.ModelAdmin):
    raw_id_fields = ['course']
    list_select_related = ['course']
    list_display = ["id", 'course', "title", "description", "is_available"]
    list_filter = ['is_available']
    list_per_page = 30
    search_fields = ['title']
    list_display_links = ['id', "course"]


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', "course", "is_publish", "created_at", "updated_at"]
    list_select_related = ['user', "course"]
    list_editable = ['is_publish']
    raw_id_fields = ['user', "course"]
    list_filter = ['created_at']
    search_fields = ['user__mobile_phone']


@admin.register(models.SectionVideo)
class SectionVideoAdmin(admin.ModelAdmin):
    raw_id_fields = ['section']
    list_display = ['section', "is_publish", "created_at"]
    list_select_related = ['section']
    list_per_page = 20
    list_filter = ['is_publish', "created_at"]


@admin.register(models.SectionFile)
class SectionFileAdmin(admin.ModelAdmin):
    raw_id_fields = ['section']
    list_display = ['section', "is_publish", "created_at"]
    list_select_related = ['section']
    list_per_page = 20
    list_filter = ['is_publish', "created_at"]


@admin.register(models.LessonCourse)
class LessonCourseAdmin(admin.ModelAdmin):
    filter_horizontal = ['students']
    list_display = ['course', "coach", "is_active", "created_at"]
    list_filter = ['is_active']
    search_fields = ['course__course_name', "coach__coach_number"]


@admin.register(models.StudentAccessCourse)
class StudentAccessCourseAdmin(admin.ModelAdmin):
    list_display = ['student', "course", "is_active", "created_at"]
    list_select_related = ['student', "course"]
    list_filter = ['is_active']
    search_fields = ['student__student_number']
    list_per_page = 20


@admin.register(models.CoachAccessCourse)
class StudentAccessCourseAdmin(admin.ModelAdmin):
    list_display = ['coach', "course", "is_active", "created_at"]
    list_select_related = ['coach', "course"]
    list_filter = ['is_active']
    search_fields = ['coach__coach_number']
    list_per_page = 20


admin.site.register(models.SendSectionFile)
