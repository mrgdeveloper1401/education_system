from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Discount, Coupon, UserCoupon


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
    list_display = ("code", "valid_from", "valid_to", "max_usage", "discount", "is_active", "created_at")
    list_editable = ("is_active", 'max_usage')
    search_fields = ("code",)
    search_help_text = _("برای سرچ کردن میتوانید کد مورد نظر رو سرچ کنید")
    list_filter = ("is_active",)

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "code",
            "valid_from",
            "valid_to",
            "discount",
            "is_active",
            "created_at",
            "max_usage"
        )


@admin.register(UserCoupon)
class UserCouponAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "coupon",
        "created_at"
    )
    raw_id_fields = (
        "user",
        "coupon"
    )
    list_per_page = 20
    search_fields = ("user__mobile_phone",)
    search_help_text = _("برای جست و جو میتوانید از شماره موبایل کاربر استفاده کنید")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "coupon").only(
            "user__mobile_phone",
            "coupon__code",
            "created_at"
        )
