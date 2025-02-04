from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin

from .models import User, Otp, State, City, Ticket, RecycleUser, Coach, Student, RequestLog


@admin.register(User)
class UserAdmin(BaseUserAdmin):
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
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
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
        q = qs.filter(is_deleted=False)
        return q


@admin.register(Otp)
class OtpAdmin(admin.ModelAdmin):
    list_display = ['mobile_phone', 'code', 'expired_date']
    search_fields = ['mobile_phone']
    list_filter = ['expired_date', "created_at"]
    date_hierarchy = 'created_at'


@admin.register(State)
class StateAdmin(ImportExportModelAdmin):
    list_display = ['id', "state_name"]
    search_fields = ['state_name']


@admin.register(City)
class CityAdmin(ImportExportModelAdmin):
    raw_id_fields = ['state']
    list_display = ['id', 'state', "city"]
    search_fields = ['city']
    list_display_links = ['id', "state", "city"]


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    raw_id_fields = ['user']
    list_display = ['user', "subject_ticket", "is_publish"]


@admin.register(RecycleUser)
class RecycleUserAdmin(admin.ModelAdmin):
    list_display = ("id", "mobile_phone", "email", "first_name", "last_name", "is_staff", "is_active", "is_superuser",
                    "is_deleted", "deleted_at")
    search_fields = ['mobile_phone']

    def get_queryset(self, request):
        return RecycleUser.objects.filter(is_deleted=True)


admin.site.register(Coach)
admin.site.register(Student)
admin.site.register(RequestLog)