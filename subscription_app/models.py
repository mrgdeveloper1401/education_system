from datetime import timedelta

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.validators import ValidationError, MinValueValidator, MaxValueValidator

from core.models import CreateMixin, UpdateMixin, SoftDeleteMixin
from course.enums import NumberOfDaysChoices
from course.models import Course
from discount_app.models import Coupon


# TODO, when clean migration remove attribute null in field user and field crud_course_type
class Subscription(CreateMixin, UpdateMixin, SoftDeleteMixin):
    class Status(models.TextChoices):
        ACTIVE = 'active', _('فعال')
        EXPIRED = 'expired', _('منقضی شده')
        PENDING = 'pending', _('در انتظار')
        CANCELED = 'canceled', _('لغو شده')
        TRIAL = 'trial', _('آزمایشی')

    user = models.ForeignKey("accounts.User", on_delete=models.DO_NOTHING, related_name="user_subscription",
                             null=True)
    course = models.ForeignKey(Course, on_delete=models.DO_NOTHING, related_name='course_subscription', null=True)
    end_date = models.DateField()
    coupon = models.ForeignKey("discount_app.Coupon", on_delete=models.DO_NOTHING, blank=True, null=True,
                                 related_name="coupon_subscription",)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    auto_renew = models.BooleanField(default=False)
    price = models.FloatField(null=True, blank=True)
    crud_course_type = models.ForeignKey("course.CourseTypeModel", on_delete=models.DO_NOTHING, null=True)

    def __str__(self):
        return f"{self.user.mobile_phone} - {self.status}"

    def final_price_by_tax_coupon(self, coupon_code):
        coupon = Coupon.objects.filter(
            is_active=True,
            valid_from__lte=timezone.now(),
            valid_to__gte=timezone.now(),
            code=coupon_code
        ).only("is_active", "valid_from", "valid_to", "code")

        tax_value = 10
        price_tax = self.price + (self.price * tax_value) / 100

        if coupon:
            get_coupon = coupon.last()
            get_coupon_percent = get_coupon.discount
            calc_discount = self.price - (self.price * get_coupon_percent) / 100
            final_price = calc_discount + (calc_discount * tax_value) / 100
            return final_price
        return price_tax

    class Meta:
        db_table = 'subscription'
        ordering = ('-created_at',)
        verbose_name = _('اشتراک')
        verbose_name_plural = _('اشتراک‌ها')


class Plan(CreateMixin, UpdateMixin, SoftDeleteMixin):
    plan_title = models.CharField(help_text=_("عنوان پلن"))
    number_of_days = models.CharField(max_length=10, choices=NumberOfDaysChoices.choices,
                                      default=NumberOfDaysChoices.one)
    price = models.FloatField(validators=[MinValueValidator(0)], help_text=_("قیمت"), blank=True, null=True)
    is_free = models.BooleanField(default=False, help_text=_("رایگان هست؟"))
    description = models.TextField(help_text=_("توضیحی در مورد پلن"))
    is_active = models.BooleanField(default=True, help_text=_("قابل انتشار باشد یا خیر"))
    facilities = ArrayField(models.CharField(max_length=50), blank=True, null=True, default=list)
    discount_percent = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        validators=[MaxValueValidator(100)],
        help_text=_("درصد تخفیف (۰ تا ۱۰۰)")
    )

    def __str__(self):
        return self.plan_title

    def clean(self):
        if self.is_free and self.price:
            raise ValidationError({"is_free", _("dont create plan when is_free and not free")})
        if not self.is_free and not self.price:
            raise ValidationError({"price": _("price and is free, one of this must bet set")})

    @property
    def calc_discount(self):
        if self.discount_percent and self.price:
            price = (self.price * self.discount_percent) / 100
            return price
        else:
            return "noting"

    @property
    def final_price(self):
        return max(self.price - self.calc_discount, 0)

    class Meta:
        db_table = 'plan'


class PaymentSubscription(CreateMixin, UpdateMixin, SoftDeleteMixin):
    subscription = models.ForeignKey(Subscription, on_delete=models.DO_NOTHING, related_name='payment_subscription')
    response_payment = models.JSONField(blank=True, null=True)

    class Meta:
        db_table = "payment_subscription"
        ordering = ("-created_at",)


# TODO, when clean migration, remove null attribute
class PaymentVerify(CreateMixin, UpdateMixin, SoftDeleteMixin):
    verify_payment = models.JSONField(blank=True)
    user = models.ForeignKey("accounts.User", on_delete=models.DO_NOTHING, related_name="user_payment_verify",
                             null=True)

    class Meta:
        db_table = "payment_verify"
        ordering = ("-created_at",)
