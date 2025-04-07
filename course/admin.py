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
    list_display = ["id", 'course', "title", "is_publish"]
    list_filter = ['created_at']
    list_per_page = 20
    search_fields = ['title']
    list_display_links = ['id', "course"]
    list_editable = ['is_publish']


@admin.register(models.Comment)
class CommentAdmin(TreeAdmin):
    list_display = ['user', "category", "is_publish", "created_at"]
    list_editable = ['is_publish']
    raw_id_fields = ['user', "category"]
    list_filter = ['is_publish']
    search_fields = ['user__mobile_phone']
    form = movenodeform_factory(models.Comment)
    list_per_page = 20


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
    list_display = ["id", 'section', "is_publish", "created_at"]
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
    list_per_page = 20
    list_filter = ['created_at']
    raw_id_fields = ['section']


@admin.register(models.PresentAbsent)
class PresentAbsentAdmin(admin.ModelAdmin):
    list_display = ['section', "student", "student_status", "created_at", "updated_at"]
    list_per_page = 20
    raw_id_fields = ['section', "student"]
    list_filter = ['student_status']
    list_editable = ['student_status']


@admin.register(models.SendSectionFile)
class SendSectionFileAdmin(admin.ModelAdmin):
    list_display = ['student', "section_file", "created_at", 'send_file_status']
    raw_id_fields = ['student', "section_file"]
    list_per_page = 20
    list_filter = ['send_file_status']


@admin.register(models.StudentAccessSection)
class StudentAccessSectionAdmin(admin.ModelAdmin):
    list_display = ['student', "section", "get_section_name", "get_section_course_name", "is_access", "created_at"]
    list_editable = ['is_access']
    list_per_page = 20
    list_filter = ['is_access']
    raw_id_fields = ['student', "section"]
    search_fields = ['student__student_number']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related(
            "student__user",
            "section__course__category"
        ).only(
            "student__student_number",
            "section__title",
            "is_access",
            "created_at",
            "section__course__course_name",
            "section__course__category__category_name",
            "student__user__first_name",
            "student__user__last_name",
        )
        return qs

    def get_section_name(self, obj):
        return obj.section.title

    def get_section_course_name(self, obj):
        return obj.section.course.course_name


@admin.register(models.OnlineLink)
class OnlineLinkAdmin(admin.ModelAdmin):
    list_display = ['class_room', "is_publish", "created_at", "updated_at"]
    raw_id_fields = ['class_room']
    list_filter = ['is_publish']
    list_per_page = 20


@admin.register(models.SectionQuestion)
class SectionQuestion(admin.ModelAdmin):
    list_display = ["question_title", "section", "is_publish", "created_at"]
    list_per_page = 20
    raw_id_fields = ['section']
    list_filter = ['is_publish']

@admin.register(models.AnswerQuestion)
class AnswerQuestionAdmin(admin.ModelAdmin):
    list_display = ['student', "section_question", "rate", "created_at"]
    list_editable = ['rate']
    list_filter = ['rate']
    list_per_page = 20
    raw_id_fields = ['student', "section_question"]


@admin.register(models.CallLessonCourse)
class CallLessonCourseAdmin(admin.ModelAdmin):
    lesson_course = ('call', "status", "call_answering", "project")
    list_filter = ('cancellation_alert',)
    search_fields = ('status', )
    list_per_page = 20
    raw_id_fields = ("lesson_course",)
    list_select_related = ("lesson_course",)

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "cancellation_alert", "call", "call_answering", "project", "phase", "call_date", "result_call",
            "lesson_course__class_name"
        )
