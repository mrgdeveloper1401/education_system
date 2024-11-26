from django.core.exceptions import ValidationError
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from accounts.validators import MobileRegexValidator
from core.models import UpdateMixin, SoftDeleteMixin, CreateMixin
from utils.model_choices import Grade, Gender


class ConsultationTopic(CreateMixin, UpdateMixin, SoftDeleteMixin):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'consultation_topic'


class ConsultationSchedule(CreateMixin, UpdateMixin, SoftDeleteMixin):
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    interval = models.PositiveSmallIntegerField(default=2)

    def __str__(self):
        return f"({self.start_date} {self.end_date}) ({self.start_time} - {self.end_time}) {self.interval}"

    def clean(self):
        if self.start_date < now().date():
            raise ValidationError(_("تاریخ شروع وارد شده کوچک تر از امروز هست"))
        elif self.end_date < now().date():
            raise ValidationError(_("تاریخ پایان وارد شده کوچک تر از امروز هست"))
        elif self.end_time < self.start_time:
            raise ValidationError(_("ساعت پایانی باید بزرگ تر از ساعت شروع باشد"))
        elif self.start_time < now().time():
            raise ValidationError(_("ساعت شروع کوچک تر از زمان حال حاضر هست"))
        return super().clean()

    def generate_slots(self):
        from datetime import timedelta, datetime

        current_date = self.start_date
        while current_date <= self.end_date:
            current_time = datetime.combine(current_date, self.start_time)
            end_time = datetime.combine(current_date, self.end_time)
            while current_time < end_time:
                next_time = current_time + timedelta(hours=self.interval)
                ConsultationSlot.objects.create(
                    schedule=self,
                    date=current_date,
                    start_time=current_time.time(),
                    end_time=next_time.time(),
                )
                current_time += timedelta(hours=self.interval)
            current_date += timedelta(days=1)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.generate_slots()

    class Meta:
        db_table = 'consultation_schedule'


class ConsultationRequest(CreateMixin, UpdateMixin, SoftDeleteMixin):
    topic = models.ForeignKey(ConsultationTopic, on_delete=models.CASCADE, related_name="consultation_request_topic")
    slot = models.ForeignKey("ConsultationSlot", on_delete=models.CASCADE, related_name="consultation_slot_slot")
    mobile_phone = models.CharField(_("شماره موبایل"), max_length=11, validators=[MobileRegexValidator()])
    first_name = models.CharField(_("نام کد اموز"), max_length=30)
    last_name = models.CharField(_("نام خانوادگی کد اموز"), max_length=30)
    classroom = models.CharField(_("پایه درسی"), choices=Grade, max_length=8)
    gender = models.CharField(_("جنسیت"), max_length=6, choices=Gender.choices)

    def __str__(self):
        return f'{self.mobile_phone} {self.first_name} {self.last_name}'

    class Meta:
        db_table = 'consultation_request'


class ConsultationSlot(CreateMixin, UpdateMixin, SoftDeleteMixin):
    schedule = models.ForeignKey(ConsultationSchedule, on_delete=models.PROTECT, related_name="consultation_slot")
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.date} {self.start_time} - {self.end_time}'

    class Meta:
        db_table = 'consultation_slot'
