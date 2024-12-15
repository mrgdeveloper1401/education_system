from django.contrib import admin

from .models import Order
# Register your models here.


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    raw_id_fields = ['user', "course"]
    list_select_related = ['user', "course"]
    list_filter = ['is_complete']
