from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Discount, Coupon


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ("content_type", "object_id", "percent", "start_date", "end_date", "is_active", "created_at")
    list_editable = ("is_active", "percent")

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "percent", "start_date", "end_date", "is_active", "created_at"
        )


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = ("code", "valid_from", "valid_to", "discount", "is_active", "created_at")
    list_editable = ("is_active",)
    search_fields = ("code",)
    search_help_text = _("برای سرچ کردن میتوانید کد مورد نظر رو سرچ کنید")
    list_filter = ("is_active", "for_first")

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "code", "valid_from", "valid_to", "discount", "is_active", "created_at"
        )
