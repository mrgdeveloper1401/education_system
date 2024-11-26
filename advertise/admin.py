from django.contrib import admin

from .models import ConsultationTopic, ConsultationRequest, ConsultationSchedule, ConsultationSlot


admin.site.register(ConsultationTopic)
admin.site.register(ConsultationRequest)
admin.site.register(ConsultationSchedule)
admin.site.register(ConsultationSlot)
