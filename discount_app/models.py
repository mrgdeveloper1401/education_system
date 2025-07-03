from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import CreateMixin, UpdateMixin, SoftDeleteMixin


class Coupon(CreateMixin, UpdateMixin, SoftDeleteMixin):
    code = models.CharField(max_length=50, unique=True)
    valid_from = models.DateTimeField(_("از تاریخ"))
    valid_to = models.DateTimeField(_("تا تاریخ"))
    max_usage = models.PositiveIntegerField(
        _("حداکثر استفاده"),
        blank=True,
        null=True,
        help_text=_("توسط کاربر چند بار استفاده شود")
    )
    discount = models.IntegerField(help_text=_("درصد کد تخفیف"),
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_active = models.BooleanField(default=True)
    for_first = models.BooleanField(default=False)

    def __str__(self):
        return self.code

    def is_valid(self):
        now = timezone.now()
        return self.is_active and (self.valid_from <= now <= self.valid_to)

    class Meta:
        db_table = "discount_coupon"
        ordering = ("-created_at",)


class Discount(CreateMixin, UpdateMixin, SoftDeleteMixin):
    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT, null=True)
    object_id = models.PositiveIntegerField(null=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    percent = models.PositiveSmallIntegerField(
        verbose_name="درصد تخفیف",
        validators=[MaxValueValidator(100), MinValueValidator(0)]
    )
    start_date = models.DateTimeField(verbose_name="تاریخ شروع تخفیف")
    end_date = models.DateTimeField(verbose_name="تاریخ پایان تخفیف")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    def __str__(self):
        return f"{self.percent}% تخفیف برای {self.content_object}"

    class Meta:
        db_table = "discount_app"
        verbose_name = "تخفیف"
        verbose_name_plural = "تخفیف‌ها"
        # unique_together = ("content_type", "object_id")
