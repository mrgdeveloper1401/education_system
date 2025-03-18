from django.contrib import admin
from treebeard.forms import movenodeform_factory
from treebeard.admin import TreeAdmin
from import_export.admin import ImportExportModelAdmin

from . import models


@admin.register(models.Course)
class CouAdmin(ImportExportModelAdmin):
    list_display = ["category", "course_name", "is_publish", "project_counter"]
    list_filter = ['created_at']
    raw_id_fields = ['category']
    list_select_related = ['category']
    search_fields = ['course_name']


@admin.register(models.Category)
class CategoryTreeAdmin(TreeAdmin, ImportExportModelAdmin):
    form = movenodeform_factory(models.Category)
    list_per_page = 20
    list_display = ['id', "category_name"]
    list_display_links = ['category_name']


@admin.register(models.Section)
class SectionAdmin(admin.ModelAdmin):
    raw_id_fields = ['course']
    list_select_related = ['course']
    list_display = ["id", 'course', "title"]
    list_filter = ['created_at']
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
    list_display = ['course', "coach", "is_active", "created_at", "progress"]
    list_filter = ['is_active']
    search_fields = ['course__course_name', "coach__coach_number", "progress"]
    raw_id_fields = ['course', "coach"]


@admin.register(models.Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['course', "student", "is_active", "created_at"]
    list_select_related = ['student', "course"]
    raw_id_fields = ['course', "student"]


@admin.register(models.StudentSectionScore)
class SectionScoreAdmin(admin.ModelAdmin):
    list_display = ['section', "score", 'created_at']
    list_per_page = 30
    list_filter = ['created_at']
    raw_id_fields = ['section', "student"]


@admin.register(models.PresentAbsent)
class PresentAbsentAdmin(admin.ModelAdmin):
    list_display = ['section', "student", "is_present"]
    list_per_page = 30
    raw_id_fields = ['section', "student"]
    list_filter = ['is_present']


@admin.register(models.SendSectionFile)
class SendSectionFileAdmin(admin.ModelAdmin):
    list_display = ['student', "section_file", "created_at"]
    raw_id_fields = ['student', "section_file"]
    list_per_page = 30


@admin.register(models.Practice)
class PracticeAdmin(admin.ModelAdmin):
    list_display = ['practice_title', "is_publish", "is_close", "start_date", "end_date", "created_at"]
    list_editable = ['is_publish']
    list_per_page = 30
    search_fields = ['practice_title']
    list_filter = ['is_publish', "created_at", "is_close"]
