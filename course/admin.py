from django.contrib import admin
from . import models


admin.site.register(models.Term)
admin.site.register(models.Comment)


@admin.register(models.Course)
class CouAdmin(admin.ModelAdmin):
    raw_id_fields = ['term']
    list_display = ['term', "course_name", "course_price", "course_duration", "is_deleted"]
    list_filter = ['created_at', "updated_at"]
    list_select_related = ['term']


@admin.register(models.Section)
class SectionAdmin(admin.ModelAdmin):
    raw_id_fields = ['course']
    list_select_related = ['course']


@admin.register(models.LessonTakenByStudent)
class LessonTakenByStudentAdmin(admin.ModelAdmin):
    list_select_related = ['course', "student"]
    raw_id_fields = ['student', "course"]


@admin.register(models.LessonTakenByCoach)
class LessonTakenByCoachAdmin(admin.ModelAdmin):
    raw_id_fields = ['coach', "course"]
    list_select_related = ['coach', "course"]
    list_display = ['coach', "course", "course__term"]

    def get_queryset(self, request):
        q = super().get_queryset(request)
        qs = q.select_related('course__term', "coach__user")
        return qs


@admin.register(models.Practice)
class PracticeAdmin(admin.ModelAdmin):
    raw_id_fields = ['coach']
    list_select_related = ['coach']
    list_display = ['coach', "is_available"]


@admin.register(models.ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    raw_id_fields = ['course']
    filter_horizontal = ['student', "coach"]
    list_filter = ['is_available']
    list_display = ['course', "course__term", "is_available"]


@admin.register(models.PracticeSubmission)
class PracticeSubmissionAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Quiz)
class QuizAdmin(admin.ModelAdmin):
    pass
