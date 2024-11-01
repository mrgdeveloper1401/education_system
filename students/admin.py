from django.contrib import admin

from .models import City, Student, State
# Register your models here.


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    pass


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    pass
