from django.contrib import admin

from .models import ConsultationTopic, ConsultationRequest, ConsultationSchedule, ConsultationSlot


admin.site.register(ConsultationTopic)

@admin.register(ConsultationSlot)
class SlotAdmin(admin.ModelAdmin):
    list_display = ("id", "date", "is_available")
    list_display_links = ("id", "date")
    list_filter = ("is_available",)
    list_editable = ("is_available",)
    raw_id_fields = ("schedule",)
    list_per_page = 20


@admin.register(ConsultationSchedule)
class ConsultationScheduleAdmin(admin.ModelAdmin):
    list_display = ("id", "start_date", "end_date", "created_at", "updated_at")
    list_per_page = 20
    list_display_links = ("id", "start_date", "end_date")


@admin.register(ConsultationRequest)
class ConsultationRequestAdmin(admin.ModelAdmin):
    raw_id_fields = ("slot",)
    list_display = ("id", "slot_id", "mobile_phone", "first_name", "last_name", "is_answer", "topic")
    list_display_links = ("id", "slot_id", "mobile_phone")
    list_filter = ("is_answer",)
    list_per_page = 20
    search_fields = ("mobile_phone",)
    search_help_text = "برای جست و جو میتوانید از شماره موبایل استفاده کنید"
