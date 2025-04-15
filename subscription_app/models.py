import datetime

from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import ValidationError, MinValueValidator, MaxValueValidator
from accounts.models import User
from core.models import CreateMixin, UpdateMixin, SoftDeleteMixin
from course.enums import NumberOfDaysChoices


class Subscription(CreateMixin, UpdateMixin, SoftDeleteMixin):
    class Status(models.TextChoices):
        ACTIVE = 'active', _('فعال')
        EXPIRED = 'expired', _('منقضی شده')
        PENDING = 'pending', _('در انتظار')
        CANCELED = 'canceled', _('لغو شده')
        TRIAL = 'trial', _('آزمایشی')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey('Plan', on_delete=models.SET_NULL, null=True, related_name='subscriptions')
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING
    )
    auto_renew = models.BooleanField(default=False)
    payment_gateway_data = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.mobile_phone} - {self.plan.plan_title if self.plan else 'No Plan'}"

    @property
    def remaining_days(self):
        today = datetime.date.today()
        if today > self.end_date:
            return 0
        return (self.end_date - today).days

    @property
    def is_expired(self):
        return datetime.date.today() > self.end_date

    def renew(self, plan=None, duration_days=None):
        if plan:
            self.plan = plan
        if duration_days:
            self.end_date = datetime.date.today() + datetime.timedelta(days=duration_days)
        self.status = self.Status.ACTIVE
        self.save()

    def cancel(self):
        self.status = self.Status.CANCELED
        self.is_active = False
        self.save()

    # def save(self, *args, **kwargs):
    #     # Update status based on dates
    #     today = datetime.date.today()
    #     if self.end_date < today:
    #         self.status = self.Status.EXPIRED
    #     elif self.created_at > today:
    #         self.status = self.Status.PENDING
    #     elif self.status != self.Status.CANCELED:
    #         self.status = self.Status.ACTIVE
    #
    #     super().save(*args, **kwargs)

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
