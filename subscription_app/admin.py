from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Subscription, PaymentSubscription


# @admin.register(Plan)
# class PlanAdmin(admin.ModelAdmin):
#     list_display = ('plan_title', 'number_of_days', 'price', "discount_percent", 'is_free', 'is_active', "calc_discount",
#                     "final_price", 'created_at')
#     list_filter = ('is_free', 'is_active', 'created_at')
#     search_fields = ('plan_title', 'description')
#     list_editable = ('is_active', "number_of_days", "discount_percent")
#     fieldsets = (
#         (None, {
#             'fields': ('plan_title', 'description')
#         }),
#         (_('Pricing'), {
#             'fields': ('price', "discount_percent", 'is_free', 'number_of_days')
#         }),
#         (_('Status'), {
#             'fields': ('is_active',)
#         }),
#     )


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    readonly_fields = ("created_at", "updated_at")
    list_display = (
        "id",
        'user',
        'created_at',
        'status',
        # "status_display",
        "price",
    )
    list_filter = ('status',)
    search_fields = ('user__mobile_phone', )
    list_select_related = ("course", "crud_course_type", "user")
    raw_id_fields = ("course", "crud_course_type", "user")
    list_editable = ("status",)
    date_hierarchy = 'created_at'
    actions = ('activate_subscriptions', 'deactivate_subscriptions', 'renew_subscriptions')
    fieldsets = (
        (None, {
            'fields': ('user', "course")
        }),
        (_('Dates'), {
            'fields': ('created_at', "updated_at", 'end_date')
        }),
        (_('Status'), {
            'fields': ('status', 'auto_renew', "price")
        }),
    )

    # def status_display(self, obj):
    #     status_colors = {
    #         'active': 'green',
    #         'expired': 'gray',
    #         'pending': 'blue',
    #         'canceled': 'red',
    #         'trial': 'purple',
    #     }
    #     color = status_colors.get(obj.status, 'black')
    #     return format_html(
    #         '<span style="color: {};">{}</span>',
    #         color,
    #         obj.get_status_display()
    #     )
    # status_display.short_description = _('Status')
    # status_display.admin_order_field = 'status'

    def get_queryset(self, request):
        return super().get_queryset(request).only(
            "created_at",
            "updated_at",
            "status",
            "user__mobile_phone",
            "course__course_name",
            "auto_renew",
            "price",
            "crud_course_type__course_type",
            "end_date",
        )


@admin.register(PaymentSubscription)
class PaymentSubscriptionAdmin(admin.ModelAdmin):
    list_display = ("subscription", "id", "created_at")
    list_per_page = 20
    raw_id_fields = ("subscription",)
