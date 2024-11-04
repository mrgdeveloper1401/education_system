from django.contrib import admin

from .models import Department
# Register your models here.


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    raw_id_fields = ['user']
    list_select_related = ['user']
    list_display = ['user', "department_name"]
    search_fields = ['department_name']
    date_hierarchy = 'created_at'
    list_filter = ['created_at', "updated_at"]
