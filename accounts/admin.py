from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Otp


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form_template = "admin/auth/user/add_form.html"
    change_user_password_template = None
    fieldsets = (
        (None, {"fields": ("mobile_phone", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_deleted",
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
                "fields": ("mobile_phone", "usable_password", "password1", "password2"),
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
    readonly_fields = ['updated_at', "deleted_at", "last_login", "created_at"]


@admin.register(Otp)
class OtpAdmin(admin.ModelAdmin):
    list_display = ['mobile_phone', 'code', 'expired_date']
    search_fields = ['mobile_phone']
    list_filter = ['expired_date', "created_at"]
    date_hierarchy = 'created_at'
