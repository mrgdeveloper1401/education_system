from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from . import models


@admin.register(models.Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ("name", "course", "start_datetime", "exam_end_date", "is_done_exam", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "course__course_name")
    list_per_page = 20
    raw_id_fields = ("course",)
    search_help_text = _("برای جست و جو میتوانید از نام ازمون استفاده کنید")
    filter_horizontal = ("user_access",)
    list_editable = ("is_active",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'course'
        ).only(
            "course__course_name",
            "name",
            "start_datetime",
            "is_active",
            "created_at",
            "description",
            "number_of_time",
            "created_at"
        )


@admin.register(models.Question)
class QuestionAdmin(admin.ModelAdmin):
    raw_id_fields = ("exam",)
    list_display = ('exam', "exam_id", "id", 'is_active', "question_type", "max_score", "created_at")
    list_per_page = 30
    list_filter = ("is_active",)
    search_fields = ("exam__name",)
    search_help_text = _("برای جست و جو کردن میتوانید از نام ازمون استفاده کنید")
    list_editable = ("question_type", "max_score", "is_active")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("exam").only(
            "is_active",
            "created_at",
            "exam__name",
            "name",
            "question_file",
            "question_type",
            "max_score"
        )


@admin.register(models.Participation)
class ParticipationAdmin(admin.ModelAdmin):
    list_display = ("student", "get_student_phone", "exam", "score", "created_at", "is_access")
    raw_id_fields = ("student", "exam")
    list_per_page = 20
    search_fields = ("exam__name", "student__student_number")
    search_help_text = _("برای جست و جو میتوانید از نام ازمون یا شماره دانشجویی استفاده کنید")
    list_editable = ("is_access",)
    list_filter = ("is_access",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            "student__user",
            "exam"
        ).only(
            "student__student_number",
            "exam__name",
            "created_at",
            "student__user__mobile_phone",
            "is_access",
            "score"
        )

    def get_student_phone(self, obj):
        return obj.student.user.mobile_phone


@admin.register(models.Choice)
class ChoiceAdmin(admin.ModelAdmin):
    raw_id_fields = ("question",)
    list_display = ("question", "is_correct", "created_at")
    list_filter = ("is_correct",)
    list_per_page = 30
    search_fields = ("question__name",)
    search_help_text = _("برای جست و جو میتوانید فیلد سوال استفاده کنید")
    list_select_related = ("question",)

@admin.register(models.Answer)
class AnswerAdmin(admin.ModelAdmin):
    raw_id_fields = ("participation", 'question')
    filter_horizontal = ("selected_choices",)
    list_display = ("participation", "given_score", "created_at")
    list_select_related = ("participation", "question")

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "participation__is_access",
            "question__name",
            "selected_choices",
            "text_answer",
            "given_score",
            "choice_file",
            "created_at"
        )
