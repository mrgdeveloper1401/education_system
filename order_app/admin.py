from django.contrib import admin

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
    list_display = ("course", "mobile_phone", "fist_name", "last_name", "created_at")
    search_fields = ("mobile_phone",)
    list_per_page = 20
    raw_id_fields = ("course",)

    def get_queryset(self, request):
        return super().get_queryset(request).defer(
            "is_deleted", "deleted_at", "updated_at"
        )
