from django.contrib import admin
from treebeard.forms import movenodeform_factory
from treebeard.admin import TreeAdmin

from . import models


@admin.register(models.Course)
class CouAdmin(admin.ModelAdmin):
    list_display = ["course_name", "course_price", "course_duration", "is_deleted"]
    list_filter = ['created_at', "updated_at"]
    raw_id_fields = ['category']
    list_select_related = ['category']


@admin.register(models.Category)
class CategoryTreeAdmin(TreeAdmin):
    form = movenodeform_factory(models.Category)


# @admin.register(models.Section)
# class SectionAdmin(admin.ModelAdmin):
#     raw_id_fields = ['course']
#     list_select_related = ['course']
#
#
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
