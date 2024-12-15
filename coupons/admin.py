from django.contrib import admin

from .models import Discount, Coupon
# Register your models here.


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    pass


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['coupon_code', "max_number", "is_active", "expired_date"]
    list_filter = ['is_active']
    search_fields = ['coupon_code']
