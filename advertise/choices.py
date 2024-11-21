from django.db import models
from django.utils.translation import gettext_lazy as _


class SubjectAdvertiseChoices(models.TextChoices):
    how_to_signup = 'how_to_signup', _("چه جوری در کلاس ها ثبت نام کنم")
    course_stat = 'course_start', _("کدام دوره رو شروع کنم")
    installment = 'installment', _("درخواست خرید قسطی")
    what_happened = 'what_happened', _("در هر جلسه چه اتفاقی می افتد")
    buy_group = "buy_group", _("درخواست خرید گروهی")
    other = 'other', _("سایز")
