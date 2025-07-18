from django.contrib import admin
from treebeard.forms import movenodeform_factory
from treebeard.admin import TreeAdmin
from import_export.admin import ImportExportModelAdmin
from django.utils.translation import gettext_lazy as _

from . import models
from .models import StudentEnrollment


class StudentEnrollmentInlineAdmin(admin.TabularInline):
    model = StudentEnrollment
    extra = 0
    raw_id_fields = ("student",)


@admin.register(models.Course)
class CouAdmin(ImportExportModelAdmin):
    list_display = ("category", "course_name", "is_publish", "is_free", "project_counter")
    list_filter = ('created_at', 'is_free')
    raw_id_fields = ('category',)
    list_select_related = ('category',)
    search_fields = ('course_name',)
    # filter_horizontal = ('plans',)


@admin.register(models.Category)
class CategoryTreeAdmin(TreeAdmin, ImportExportModelAdmin):
    form = movenodeform_factory(models.Category)
    list_per_page = 20
    list_display = ['id', "category_name"]
    list_display_links = ['category_name']


@admin.register(models.Section)
class SectionAdmin(admin.ModelAdmin):
    raw_id_fields = ('course',)
    list_select_related = ('course',)
    list_display = ("id", 'course', "title", "is_publish")
    list_filter = ('created_at', "is_last_section")
    list_per_page = 20
    search_fields = ('title',)
    list_display_links = ('id', "course")
    list_editable = ('is_publish',)


@admin.register(models.Comment)
class CommentAdmin(TreeAdmin):
    list_display = ['user', "id", "category", "is_publish", "created_at"]
    list_editable = ['is_publish']
    raw_id_fields = ['user', "category"]
    list_filter = ['is_publish']
    search_fields = ['user__mobile_phone']
    form = movenodeform_factory(models.Comment)
    list_per_page = 20


@admin.register(models.SectionVideo)
class SectionVideoAdmin(admin.ModelAdmin):
    raw_id_fields = ('section',)
    list_display = ('section', "is_publish", "created_at")
    list_select_related = ('section',)
    list_per_page = 20
    list_filter = ('is_publish', "created_at")

    def get_queryset(self, request):
        return super().get_queryset(request).defer(
            "is_deleted",
            "deleted_at"
        )


@admin.register(models.SectionFile)
class SectionFileAdmin(admin.ModelAdmin):
    raw_id_fields = ('section',)
    list_display = ("id", 'section', "is_publish", "created_at")
    list_select_related = ('section',)
    list_per_page = 20
    list_filter = ('is_publish', "created_at")
    list_display_links = ("id", "section")


@admin.register(models.LessonCourse)
class LessonCourseAdmin(admin.ModelAdmin):
    list_display = ("id", 'course', "coach", "is_active", "created_at", "progress")
    list_filter = ('is_active', "progress")
    search_fields = ('course__course_name', )
    raw_id_fields = ('course', "coach")
    list_per_page = 20
    list_select_related = ("course", "coach")
    list_display_links = ("id", "course")
    search_help_text = "برای جست و جو از نام دوره استفاده کنید"
    inlines = (StudentEnrollmentInlineAdmin,)

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "course__course_name",
            "is_active",
            "created_at",
            "progress",
            "coach__coach_number",
            "students",
            "class_name"
        )

@admin.register(models.Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('section', "student", "created_at")
    list_select_related = ('student', "section")
    raw_id_fields = ('section', "student",)

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "section_id",
            "student__student_number",
            "is_active",
            "final_pdf",
            "qr_code",
            "unique_code",
            "created_at",
        )

@admin.register(models.StudentSectionScore)
class SectionScoreAdmin(admin.ModelAdmin):
    list_display = ('section', "score", 'created_at')
    list_per_page = 20
    list_filter = ('created_at',)
    raw_id_fields = ('section', "student")


@admin.register(models.PresentAbsent)
class PresentAbsentAdmin(admin.ModelAdmin):
    list_display = ('section', "student", "student_status", "created_at", "updated_at")
    list_per_page = 20
    raw_id_fields = ('section', "student")
    list_filter = ('student_status',)
    list_editable = ('student_status',)


@admin.register(models.SendSectionFile)
class SendSectionFileAdmin(admin.ModelAdmin):
    list_display = ('student', "section_file", "created_at", 'send_file_status')
    raw_id_fields = ('student', "section_file")
    list_per_page = 20
    list_filter = ('send_file_status',)


@admin.register(models.StudentAccessSection)
class StudentAccessSectionAdmin(admin.ModelAdmin):
    list_display = ('student', "section", "get_section_name", "get_section_course_name", "is_access", "created_at")
    list_editable = ('is_access',)
    list_per_page = 20
    list_filter = ('is_access',)
    raw_id_fields = ('student', "section")
    search_fields = ('student__student_number',)

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
    raw_id_fields = ("lesson_course", "student")
    list_select_related = ("lesson_course", "student")

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "cancellation_alert", "call", "call_answering", "project", "call_date", "result_call",
            "lesson_course__class_name", "student__student_number"
        )


@admin.register(models.SignupCourse)
class SignupCourseAdmin(admin.ModelAdmin):
    list_display = ("course", "student_name", "phone_number", "created_at")
    search_fields = ("student_name",)
    list_per_page = 20
    raw_id_fields = ("course",)
    list_select_related = ("course",)

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "course__course_name",
            "student_name",
            "phone_number",
            "created_at"
        )


@admin.register(models.CourseTypeModel)
class CourseTypeModelAdmin(admin.ModelAdmin):
    raw_id_fields = ("course",)
    list_display = ("course", "id", "course_type", "price", "is_active", "plan_type", "amount")
    list_select_related = ("course",)
    list_editable = ("course_type", "is_active", "plan_type", "amount")
    list_per_page = 20
    list_filter = ("is_active",)
    search_fields = ("course__course_name",)
    search_help_text = _("برای سرچ کردن میتواند از نام دوره استفاده کنید")

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "course__course_name",
            "price",
            "is_active",
            "amount",
            "plan_type",
            "is_active",
            "description",
            "created_at",
            "course_type"
        )


@admin.register(models.StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "student_status", "created_at", "updated_at")
    list_select_related = ("student", 'lesson_course')
    list_per_page = 20
    list_filter = ("student_status",)
    raw_id_fields = ("student", "lesson_course")

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "student_status", "created_at", "updated_at", "student__referral_code", "lesson_course__class_name"
        )


@admin.register(models.CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    list_display = ("template_image", "is_active", "created_at", "updated_at")
    list_filter = ('is_active',)
    list_editable = ("is_active",)
    list_per_page = 20

    def get_queryset(self, request):
        return super().get_queryset(request).defer(
            "is_deleted",
            "deleted_at",
        )
