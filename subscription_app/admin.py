from django.contrib import admin

from . import models
from .forms import SubscriptionForm


# Register your models here.


@admin.register(models.Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    form = SubscriptionForm
    list_display = ['user', "id", "start_date", "end_date", "is_active", "number_of_day", "status"]
    search_fields = ['user__mobile_phone']
    list_select_related = ['user']
    list_per_page = 20
    list_filter = ['is_active', "status"]
    raw_id_fields = ['user']


@admin.register(models.Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['plan_title', "number_of_days", "price", "is_free", "is_active", "created_at"]
    search_fields = ['plan_title']
    list_filter = ['is_free', "is_active", "updated_at"]
    list_per_page = 20
    list_editable = ['is_active', "price", "is_free"]


@admin.register(models.AccessCourse)
class AccessCourseAdmin(admin.ModelAdmin):
    list_display = ['user', "course", "is_active"]
    list_select_related = ['user', "course"]
    raw_id_fields = ['user', "course"]
