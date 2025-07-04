from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from . import models


@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("course", "price", "mobile_phone", "created_at")
    search_fields = ("course__course_name",)
    list_per_page = 20
    search_help_text = "برای جست و جو میتوانید از نام دور کنید"
    list_select_related = ("course",)
    raw_id_fields = ("course",)

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "course__course_name", "price", "mobile_phone", "created_at", "updated_at"
        )


@admin.register(models.CourseSignUp)
class CourseSignUpAdmin(admin.ModelAdmin):
    list_display = ("course", "mobile_phone", "first_name", "last_name", "created_at", "have_account")
    search_fields = ("mobile_phone",)
    list_per_page = 20
    raw_id_fields = ("course",)
    search_help_text = _("برای جست و جو میتوانید از شماره موبایل استفاده کنید")

    def get_queryset(self, request):
        return super().get_queryset(request).defer(
            "is_deleted", "deleted_at", "updated_at"
        )


# @admin.register(models.Payment)
# class PaymentAdmin(admin.ModelAdmin):
#     list_display = ("course", "user", "price", "created_at")
#     list_select_related = ("course", "user")
#     search_fields = ("user__mobile_phone",)
#     list_per_page = 20
#     raw_id_fields = ("user", "course")
#
#     def get_queryset(self, request):
#         return super().get_queryset(request).only(
#             "course__course_name", "user__mobile_phone", "price", "created_at"
#         )
