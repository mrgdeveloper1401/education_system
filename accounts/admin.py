from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Otp, State, City, School


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form_template = "admin/auth/user/add_form.html"
    change_user_password_template = None
    fieldsets = (
        (None, {"fields": ("mobile_phone", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "gender", "school", "state", "city",
                                         "second_mobile_phone", "image", "nation_code", "address", "grade", "birth_date")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_deleted",
                    "is_coach",
                    "is_student",
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
                           "is_student", "is_coach", "first_name", "last_name"),
            },
        ),
    )
    list_display = ("mobile_phone", "email", "first_name", "last_name", "is_staff", "is_active", "is_superuser",
                    "is_deleted")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("mobile_phone", "first_name", "last_name", "email")
    ordering = ("-created_at",)
    filter_horizontal = (
        "groups",
        "user_permissions",
    )
    readonly_fields = ['updated_at', "deleted_at", "last_login", "created_at", "is_deleted"]
    list_editable = ['is_active', "is_staff", "is_superuser"]
    raw_id_fields = ["city", "state", "school"]


@admin.register(Otp)
class OtpAdmin(admin.ModelAdmin):
    list_display = ['mobile_phone', 'code', 'expired_date']
    search_fields = ['mobile_phone']
    list_filter = ['expired_date', "created_at"]
    date_hierarchy = 'created_at'


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    pass


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    raw_id_fields = ['state_name']
    list_display = ['state_name', "city"]


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['school_name', "created_at"]
