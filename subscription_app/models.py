from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import ValidationError, MinValueValidator, MaxValueValidator

from accounts.validators import MobileRegexValidator
from core.models import CreateMixin, UpdateMixin, SoftDeleteMixin
from course.enums import NumberOfDaysChoices
from course.models import Course


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
    # start_date = models.DateField(null=True)
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
