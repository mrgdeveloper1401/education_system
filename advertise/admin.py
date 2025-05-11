from django.contrib import admin

from .models import ConsultationTopic, ConsultationRequest, ConsultationSchedule, ConsultationSlot

class SlotAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "is_available")
    list_per_page = 20


admin.site.register(ConsultationTopic)
admin.site.register(ConsultationRequest)
admin.site.register(ConsultationSchedule)
admin.site.register(ConsultationSlot, SlotAdmin)
