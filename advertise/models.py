from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.validators import MobileRegexValidator
from advertise.choices import SubjectAdvertiseChoices
from core.models import UpdateMixin, SoftDeleteMixin, CreateMixin


class Advertise(UpdateMixin, SoftDeleteMixin, CreateMixin):
    is_available = models.BooleanField(_("قابل رزرو"), default=True)


class UserAdvertise(UpdateMixin, SoftDeleteMixin, CreateMixin):
    slot = models.ForeignKey('Advertise', on_delete=models.PROTECT, related_name="advertise",
                             verbose_name=_("تاریخ مشاوره"), limit_choices_to={'is_available': True})
    mobile_phone = models.CharField(_("شماره موبایل"), max_length=11, validators=[MobileRegexValidator])

    subject_advertise = models.CharField(_("موضوع مشاوره"), max_length=13, choices=SubjectAdvertiseChoices.choices)
    answered = models.BooleanField(_("پاسخ داده شد"), default=False)

    def __str__(self):
        return f'{self.mobile_phone} {self.mobile_phone} {self.subject_advertise} {self.answered}'

    class Meta:
        db_table = 'advertise'
        verbose_name = _("مشاوره")
        verbose_name_plural = _("مشاوره ها")


class IntervalAdvertise(CreateMixin, UpdateMixin, SoftDeleteMixin):
    date = models.DateField(_("تاریخ مشاوره"), unique=True)
    start_time = models.TimeField(_("ساعت شروع"))
    end_time = models.TimeField(_("ساعت پایان"))
    interval_minutes = models.PositiveSmallIntegerField(_('بازه های زمانی مشاوره'), default=120)

    def __str__(self):
        return f'{self.date} {self.start_time} {self.end_time} {self.interval_minutes}'

    class Meta:
        db_table = 'define_advertise'
        verbose_name = _("بازه زمانی مشاوره")
        verbose_name_plural = _("بازه های زمانی مشاوره")


class AnsweredAdvertise(UserAdvertise):
    class Meta:
        proxy = True
        verbose_name = _("مشاوره پاسخ داده شده")
        verbose_name_plural = _("مشاوره های پاسخ داده شده")
