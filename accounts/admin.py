from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from . import models


@admin.register(models.User)
class UserAdmin(ImportExportModelAdmin, BaseUserAdmin):
    add_form_template = "admin/auth/user/add_form.html"
    change_user_password_template = None
    fieldsets = (
        (None, {"fields": ("mobile_phone", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "gender", "state", "city", "school",
                                         "second_mobile_phone", "image", "nation_code", "address", "grade",
                                         "birth_date")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_deleted",
                    "is_coach",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "created_at", "updated_at", "deleted_at")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("mobile_phone", "usable_password", "password1", "password2", "is_active", "is_staff",
                           "is_coach", "first_name", "last_name"),
            },
        ),
    )
    list_display = ("id", "mobile_phone", "email", "first_name", "last_name", "is_staff", "is_active", "is_superuser",
                    "is_deleted", "deleted_at", "is_student", "is_coach")
    list_filter = ("is_staff", "is_superuser", "is_active", "is_coach")
    search_fields = ("mobile_phone", "first_name", "last_name", "email", "nation_code")
    ordering = ("-created_at",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )
    readonly_fields = ['updated_at', "deleted_at", "last_login", "created_at", "is_deleted"]
    list_editable = ['is_active', "is_staff", "is_superuser"]
    raw_id_fields = ["city", "state"]
    list_display_links = ['id', "mobile_phone"]
    list_per_page = 20

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        q = qs.filter(Q(is_deleted=False) | Q(is_deleted__isnull=True))
        return q


@admin.register(models.Otp)
class OtpAdmin(admin.ModelAdmin):
    list_display = ['mobile_phone', 'code', 'expired_date']
    search_fields = ['mobile_phone']
    list_filter = ['expired_date', "created_at"]
    date_hierarchy = 'created_at'


@admin.register(models.State)
class StateAdmin(ImportExportModelAdmin):
    list_display = ['id', "state_name"]
    search_fields = ['state_name']


@admin.register(models.City)
class CityAdmin(ImportExportModelAdmin):
    raw_id_fields = ['state']
    list_display = ['id', 'state', "city"]
    search_fields = ['city']
    list_display_links = ['id', "state", "city"]


@admin.register(models.Ticket)
class TicketAdmin(TreeAdmin):
    raw_id_fields = ['sender', "room"]
    list_display = ["id", 'sender', "is_publish", "created_at"]
    list_select_related = ['sender']
    list_per_page = 30
    search_fields = ['user__mobile_phone', "subject_title"]
    form = movenodeform_factory(models.Ticket)


@admin.register(models.RecycleUser)
class RecycleUserAdmin(admin.ModelAdmin):
    list_display = ("id", "mobile_phone", "email", "first_name", "last_name", "is_staff", "is_active", "is_superuser",
                    "is_deleted", "deleted_at")
    search_fields = ['mobile_phone']
    actions = ["restore_user"]

    def get_queryset(self, request):
        return models.RecycleUser.objects.filter(is_deleted=True)

    @admin.action(description="recovery user")
    def restore_user(self, request, queryset):
        return queryset.update(is_deleted=False, deleted_at=None)


@admin.register(models.TicketRoom)
class TicketRoomAdmin(admin.ModelAdmin):
    raw_id_fields = ['user']
    list_display = ["id", 'user', "title_room", "is_active", "is_close", "created_at"]
    list_filter = ['is_active', "is_close"]
    list_per_page = 20
    list_select_related = ['user']
    list_editable = ['is_active', "is_close"]
    search_fields = ['title_room']
    list_display_links = ['id', "user"]

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "user__mobile_phone", "title_room", "is_active", "is_close", "created_at"
        )


class BestStudentAdmin(ImportExportModelAdmin):
    list_display = ['id', "student", "is_publish", "created_at"]
    list_per_page = 20
    list_filter = ['is_publish']

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "id", "is_publish", "created_at", "student"
        )


@admin.register(models.Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['user', "id", "student_number", "created_at", "get_student_name"]
    raw_id_fields = ['user']
    list_filter = ['created_at']
    list_per_page = 20
    search_fields = ['user__mobile_phone', "student_number"]

    def get_student_name(self, obj):
        return obj.user.get_full_name

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "user", "student_number", "created_at", "user__first_name", "user__last_name", "user__mobile_phone"
        )


@admin.register(models.Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ['user', "coach_number", "created_at", "get_coach_name"]
    raw_id_fields = ['user']
    list_per_page = 20
    search_fields = ['user__mobile_phone', "coach_number"]

    def get_coach_name(self, obj):
        return obj.user.get_full_name

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "user", "coach_number", "created_at", "user__first_name", "user__last_name", "user__mobile_phone"
        )


@admin.register(models.BestStudent)
class BestStudentAdmin(admin.ModelAdmin):
    pass


@admin.register(models.PrivateNotification)
class PrivateNotificationAdmin(admin.ModelAdmin):
    list_display = ('user', "is_read", "created_at")
    raw_id_fields = ('user',)
    list_per_page = 20
    list_editable = ("is_read",)
    search_fields = ("user__mobile_phone",)
    search_help_text = "برای جست و جو میتوانید از شماره موبایل کاربر استفاده کنید"
    list_filter = ("is_read",)
    list_select_related = ("user",)

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "user__mobile_phone", "is_read", "created_at", "body", "title"
        )


@admin.register(models.Invitation)
class InvitationAdmin(admin.ModelAdmin):
    list_display = ("from_student", "to_student", "created_at")
    list_select_related = ('from_student', "to_student")
    list_per_page = 20

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "from_student__student_number",
            "to_student__student_number",
            "created_at"
        )
