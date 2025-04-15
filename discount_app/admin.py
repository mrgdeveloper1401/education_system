from django.contrib import admin

from .models import Discount, Coupon
# Register your models here.


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ("course", "percent", "start_date", "end_date", "is_active", "created_at")
    list_editable = ("is_active", "percent")
    search_fields = ("course__course_name",)
    list_select_related = ("course",)
    raw_id_fields = ("course",)
    search_help_text = "برای سرچ کردن میتوانید نام دوره استفاده کنید"

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "course__course_name", "percent", "start_date", "end_date", "is_active", "created_at"
        )


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ("code", "valid_from", "valid_to", "discount", "is_active", "created_at")
    list_editable = ("is_active",)
    search_fields = ("code",)
    search_help_text = "برای سرچ کردن میتوانید کد مورد نظر رو سرچ کنید"

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "code", "valid_from", "valid_to", "discount", "is_active", "created_at"
        )
