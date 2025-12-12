from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from accounts.validators import MobileRegexValidator
from advertise.managers import PublishSlotManager
from core.models import UpdateMixin, SoftDeleteMixin, CreateMixin


class ConsultationTopic(CreateMixin, UpdateMixin, SoftDeleteMixin):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'consultation_topic'


class ConsultationSchedule(CreateMixin, UpdateMixin, SoftDeleteMixin):
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return f"({self.start_date} {self.end_date})"

    def clean(self):
        if self.start_date < now().date():
            raise ValidationError(_("تاریخ شروع وارد شده کوچک تر از امروز هست"))
        elif self.end_date < now().date():
            raise ValidationError(_("تاریخ پایان وارد شده کوچک تر از امروز هست"))
        return super().clean()

    def generate_slots(self):
        from datetime import timedelta
        slot_object = []
        current_date = self.start_date
        while current_date <= self.end_date:
            if not ConsultationSlot.objects.filter(date=current_date).exists():
                slot_object.append(
                    ConsultationSlot(
                        schedule=self,
                        date=current_date,
                    )
                )
            current_date += timedelta(days=1)
        with transaction.atomic():
            ConsultationSlot.objects.bulk_create(slot_object)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.generate_slots()

    class Meta:
        db_table = 'consultation_schedule'


class ConsultationRequest(CreateMixin, UpdateMixin, SoftDeleteMixin):
    slot = models.ForeignKey("ConsultationSlot", on_delete=models.DO_NOTHING, related_name="consultation_slot_slot")
    mobile_phone = models.CharField(_("شماره موبایل"), max_length=11, validators=[MobileRegexValidator()])
    first_name = models.CharField(_("نام کد اموز"), max_length=30)
    last_name = models.CharField(_("نام خانوادگی کد اموز"), max_length=30)
    is_answer = models.BooleanField(default=False)
    topic = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f'{self.mobile_phone} {self.first_name} {self.last_name}'

    class Meta:
        db_table = 'consultation_request'
        ordering = ('-created_at',)


class ConsultationSlot(CreateMixin, UpdateMixin, SoftDeleteMixin):
    schedule = models.ForeignKey(ConsultationSchedule, on_delete=models.DO_NOTHING, related_name="consultation_slot")
    date = models.DateField()
    is_available = models.BooleanField(default=True)

    objects = PublishSlotManager()

    # def __str__(self):
    #     return f'{self.date} {self.is_available}'

    class Meta:
        db_table = 'consultation_slot'
