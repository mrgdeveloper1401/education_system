from django.contrib import admin

from . import models
# Register your models here.


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', "start_date", "end_date", "is_active", "number_of_day", "status"]
    search_fields = ['user__mobile_phone']
    list_select_related = ['user']
    list_per_page = 20
    list_editable = ['is_active', "status"]
    list_filter = ['is_active', "status"]
    raw_id_fields = ['user']
