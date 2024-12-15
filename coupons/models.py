from django.db import models
from core.models import UpdateMixin, SoftDeleteMixin, CreateMixin
from django.core.validators import ValidationError, MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from accounts.validators import MobileRegexValidator


class Coupon(UpdateMixin, SoftDeleteMixin, CreateMixin):
    mobile_phone = models.CharField(_("شماره همراه"), max_length=11, blank=True, null=True)
    coupon_code = models.CharField(_("کد کوپن"), max_length=15, unique=True, blank=True,
                                   help_text=_("کد کوپن که در صورت وارد نکردن به صورت رندوم تولید خواهد شد"
                                               "به این توجه داشته باشید که این ها حتما باید یکتا باشد"))
    max_number = models.PositiveSmallIntegerField(default=1, validators=[MinValueValidator(1)],
                                                  help_text=_("حداکثر استفاده از کوپن"))
    number_of_uses = models.PositiveSmallIntegerField(default=0, validators=[MinValueValidator(1)],
                                                      help_text=_("تعداد استقاده شده از کوپن"))
    is_active = models.BooleanField(default=True)
    expired_date = models.DateTimeField(_(" تاریخ انقضا"), null=True, blank=True)

    def __str__(self):
        return self.coupon_code

    @property
    def generate_code(self):
        from uuid import uuid4
        code = str(uuid4().hex)[:15]
        return code

    @property
    def expired_coupon(self):
        return self.expired_date < timezone.now()

    @property
    def max_number_of_uses(self):
        return self.number_of_uses >= self.max_number

    def save(self, *args, **kwargs):
        if not self.coupon_code:
            self.coupon_code = self.generate_code
        return super().save(*args, **kwargs)


class Discount(UpdateMixin, SoftDeleteMixin, CreateMixin):
    course = models.ForeignKey('course.Course', on_delete=models.DO_NOTHING, related_name='discounts')
    amount = models.FloatField()
    is_percent = models.BooleanField(default=True)
    is_value = models.BooleanField(default=False)

    @property
    def generate_price(self):
        if self.is_percent:
            price = (self.amount * self.course.course_price) / 100
        elif self.is_value:
            price = (self.course.course_price - self.amount)
        else:
            price = self.course.course_price
        return max(price, 0)

    def save(self, *args, **kwargs):
        if self.is_value and self.is_percent:
            raise ValidationError({"is_percent": _("نمیتواند مقدار درصدی و مقدار عددی رو با هم ست کنید")})
        return super().save(*args, **kwargs)
