from django.contrib import admin
from treebeard.admin import TreeAdmin
from treebeard.forms import movenodeform_factory

from .models import Term, Course, UnitSelection


# Register your models here.


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    raw_id_fields = ['department']
    list_display = ['start_date', "end_date", "term_number", "created_at", "updated_at"]
    date_hierarchy = 'created_at'
    list_filter = ['term_number', "created_at", "updated_at"]
    list_editable = ['term_number']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['department', "course_name", "is_publish", "created_at", "updated_at"]
    search_fields = ['course_name']
    list_filter = ['created_at', "updated_at", "is_publish"]
    raw_id_fields = ['department', "term"]
    list_editable = ['is_publish']


@admin.register(UnitSelection)
class UnitSelectionAdmin(admin.ModelAdmin):
    pass
