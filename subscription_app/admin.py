# import datetime
#
# from django.contrib import admin
# from django.utils.html import format_html
# from django.utils.translation import gettext_lazy as _
# from .models import Subscription, Plan
#
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
#
#
# @admin.register(Subscription)
# class SubscriptionAdmin(admin.ModelAdmin):
#     readonly_fields = ("created_at",)
#     list_display = (
#         'user_info',
#         'plan_info',
#         'created_at',
#         'end_date',
#         'remaining_days_display',
#         'status_display',
#         'is_active',
#     )
#     list_filter = ('status', 'is_active',)
#     search_fields = ('user__mobile_phone', "user__first_name", "user__last_name")
#     list_select_related = ('user', 'plan')
#     raw_id_fields = ('user', "plan")
#     date_hierarchy = 'created_at'
#     actions = ('activate_subscriptions', 'deactivate_subscriptions', 'renew_subscriptions')
#     fieldsets = (
#         (None, {
#             'fields': ('user', 'plan')
#         }),
#         (_('Dates'), {
#             'fields': ('created_at', 'end_date')
#         }),
#         (_('Status'), {
#             'fields': ('status', 'is_active', 'auto_renew')
#         }),
#         (_('Payment'), {
#             'fields': ('payment_gateway_data',),
#             'classes': ('collapse',)
#         }),
#     )
#
#     def user_info(self, obj):
#         return format_html(
#             '{}<br><small>{}</small>',
#             obj.user.get_full_name or obj.user.mobile_phone,
#             obj.user.email
#         )
#     user_info.short_description = _('User')
#     user_info.admin_order_field = 'user__email'
#
#     def plan_info(self, obj):
#         if obj.plan:
#             return format_html(
#                 '{}<br><small>{} days - {}{}</small>',
#                 obj.plan.plan_title,
#                 obj.plan.number_of_days,
#                 'Free' if obj.plan.is_free else f'${obj.plan.price}',
#                 ' (Trial)' if obj.status == Subscription.Status.TRIAL else ''
#             )
#         return '-'
#     plan_info.short_description = _('Plan')
#     plan_info.admin_order_field = 'plan__plan_title'
#
#     def remaining_days_display(self, obj):
#         remaining = obj.remaining_days
#         if remaining == 0:
#             return format_html('<span style="color: red;">{}</span>', _('Expired'))
#         elif remaining <= 7:
#             return format_html('<span style="color: orange;">{} {}</span>', remaining, _('days left'))
#         return format_html('<span style="color: green;">{} {}</span>', remaining, _('days left'))
#     remaining_days_display.short_description = _('Remaining')
#     remaining_days_display.admin_order_field = 'end_date'
#
#     def status_display(self, obj):
#         status_colors = {
#             'active': 'green',
#             'expired': 'gray',
#             'pending': 'blue',
#             'canceled': 'red',
#             'trial': 'purple',
#         }
#         color = status_colors.get(obj.status, 'black')
#         return format_html(
#             '<span style="color: {};">{}</span>',
#             color,
#             obj.get_status_display()
#         )
#     status_display.short_description = _('Status')
#     status_display.admin_order_field = 'status'
#
#     @admin.action(description=_('Activate selected subscriptions'))
#     def activate_subscriptions(self, request, queryset):
#         updated = queryset.update(is_active=True)
#         self.message_user(request, f'{updated} subscriptions activated.')
#
#     @admin.action(description=_('Deactivate selected subscriptions'))
#     def deactivate_subscriptions(self, request, queryset):
#         updated = queryset.update(is_active=False, status=Subscription.Status.CANCELED)
#         self.message_user(request, f'{updated} subscriptions deactivated.')
#
#     @admin.action(description=_('Renew selected subscriptions for 30 days'))
#     def renew_subscriptions(self, request, queryset):
#         renewed = 0
#         for subscription in queryset:
#             subscription.end_date += datetime.timedelta(days=30)
#             subscription.status = Subscription.Status.ACTIVE
#             subscription.save()
#             renewed += 1
#         self.message_user(request, f'{renewed} subscriptions renewed for 30 days.')
#
#     def get_queryset(self, request):
#         return super().get_queryset(request).select_related('user', 'plan')
