from django.db import models
from core.models import UpdateMixin, SoftDeleteMixin, CreateMixin
from django.core.validators import ValidationError
from django.utils.translation import gettext_lazy as _


class Coupon(UpdateMixin, SoftDeleteMixin, CreateMixin):
    coupon_code = models.CharField(max_length=15, unique=True)
    max_number = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.coupon_code

    @property
    def generate_code(self):
        from uuid import uuid4
        code = str(uuid4().hex)[:15]
        return code

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
