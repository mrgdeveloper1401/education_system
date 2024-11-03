from django.contrib import admin

from .models import Advertise, DefineAdvertise, AnsweredAdvertise
# Register your models here.


@admin.register(Advertise)
class AdvertiseAdmin(admin.ModelAdmin):
    raw_id_fields = ['slot']
    list_display = ['slot', "mobile_phone", "subject_advertise", "answered"]
    list_editable = ['answered', 'subject_advertise']
    search_fields = ['mobile_phone']
    date_hierarchy = 'created_at'
    list_filter = ['created_at']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(answered=False)


@admin.register(DefineAdvertise)
class DefineAdvertiseAdmin(admin.ModelAdmin):
    list_display = ['date', "start_time", "end_time", "is_available"]
    list_filter = ['is_available']
    date_hierarchy = 'date'


@admin.register(AnsweredAdvertise)
class AnsweredAdvertiseAdmin(admin.ModelAdmin):
    raw_id_fields = ['slot']
    list_display = ['slot', "mobile_phone", "subject_advertise", "answered"]
    search_fields = ['mobile_phone']
    date_hierarchy = 'created_at'
    list_filter = ['created_at']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(answered=True)


