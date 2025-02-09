from django.contrib import admin
from treebeard.forms import movenodeform_factory
from treebeard.admin import TreeAdmin
from import_export.admin import ImportExportModelAdmin

from . import models


class SectionImageInline(admin.TabularInline):
    model = models.SectionImage
    extra = 0
    raw_id_fields = ['image']


@admin.register(models.Course)
class CouAdmin(ImportExportModelAdmin):
    list_display = ["course_name", "course_price", "course_duration"]
    list_filter = ['created_at']
    raw_id_fields = ['category']
    list_select_related = ['category']
    search_fields = ['course_name']


@admin.register(models.Category)
class CategoryTreeAdmin(TreeAdmin, ImportExportModelAdmin):
    form = movenodeform_factory(models.Category)


@admin.register(models.Section)
class SectionAdmin(admin.ModelAdmin):
    raw_id_fields = ['course']
    list_select_related = ['course']
    list_display = ["id", 'course', "title", "description", "is_available"]
    list_filter = ['is_available']
    list_per_page = 30
    search_fields = ['title']
    list_display_links = ['id', "course"]
    inlines = [SectionImageInline]


@admin.register(models.SectionImage)
class SectionImageAdmin(admin.ModelAdmin):
    raw_id_fields = ['section', "image"]


# @admin.register(models.LessonTakenByStudent)
# class LessonTakenByStudentAdmin(admin.ModelAdmin):
#     list_select_related = ['course', "student"]
#     raw_id_fields = ['student', "course"]
#
#
# @admin.register(models.LessonTakenByCoach)
# class LessonTakenByCoachAdmin(admin.ModelAdmin):
#     raw_id_fields = ['coach', "course"]
#     list_select_related = ['coach', "course"]
#     list_display = ['coach', "course", "course__term"]
#
#     def get_queryset(self, request):
#         q = super().get_queryset(request)
#         qs = q.select_related('course__term', "coach__user")
#         return qs
#
#
# @admin.register(models.Practice)
# class PracticeAdmin(admin.ModelAdmin):
#     raw_id_fields = ['coach']
#     list_select_related = ['coach']
#     list_display = ['coach', "is_available"]
#
#
# @admin.register(models.ClassRoom)
# class ClassRoomAdmin(admin.ModelAdmin):
#     raw_id_fields = ['course']
#     filter_horizontal = ['student', "coach"]
#     list_filter = ['is_available']
#     list_display = ['course', "course__term", "is_available"]
#
#
# @admin.register(models.PracticeSubmission)
# class PracticeSubmissionAdmin(admin.ModelAdmin):
#     pass
#
#
# @admin.register(models.Quiz)
# class QuizAdmin(admin.ModelAdmin):
#     pass


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', "course", "is_publish", "created_at", "updated_at"]
    list_select_related = ['user', "course"]
    list_editable = ['is_publish']
    raw_id_fields = ['user', "course"]
    list_filter = ['created_at']
    search_fields = ['user__mobile_phone']