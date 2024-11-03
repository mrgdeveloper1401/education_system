from turtle import mode

from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import UpdateMixin, SoftDeleteMixin, CreateMixin


class Advertise(UpdateMixin, SoftDeleteMixin, CreateMixin):
    slot = models.ForeignKey('DefineAdvertise', on_delete=models.PROTECT, related_name="advertise",
                             verbose_name=_("تاریخ مشاوره"), limit_choices_to={'is_available': True})
    mobile_phone = models.CharField(_("شماره موبایل"))

    class SubjectAdvertiseChoices(models.TextChoices):
        how_to_signup = 'how_to_signup', _("چه جوری در کلاس ها ثبت نام کنم")
        course_stat = 'course_start', _("کدام دوره رو شروع کنم")
        installment = 'installment', _("درخواست خرید قسطی")
        what_happened = 'what_happened', _("در هر جلسه چه اتفاقی می افتد")
        buy_group = "buy_group", _("درخواست خرید گروهی")
        other = 'other', _("سایز")
    subject_advertise = models.CharField(_("موضوع مشاوره"), max_length=13, choices=SubjectAdvertiseChoices.choices)
    answered = models.BooleanField(_("پاسخ داده شد"), default=False)

    def __str__(self):
        return f'{self.mobile_phone} {self.mobile_phone} {self.subject_advertise} {self.answered}'

    class Meta:
        db_table = 'advertise'
        verbose_name = _("مشاوره")
        verbose_name_plural = _("مشاوره ها")


class DefineAdvertise(CreateMixin, UpdateMixin, SoftDeleteMixin):
    date = models.DateField(_("تاریخ مشاوره"))
    start_time = models.TimeField(_("ساعت شروع"))
    end_time = models.TimeField(_("ساعت پایان"))
    is_available = models.BooleanField(_("قابل رزرو"), default=True)

    def __str__(self):
        return f'{self.date} {self.is_available}'

    class Meta:
        db_table = 'define_advertise'
        verbose_name = _("بازه زمانی مشاوره")
        verbose_name_plural = _("بازه های زمانی مشاوره")


class AnsweredAdvertise(Advertise):
    class Meta:
        proxy = True
        verbose_name = _("مشاوره پاسخ داده شده")
        verbose_name_plural = _("مشاوره های پاسخ داده شده")
