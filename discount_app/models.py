from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from core.models import CreateMixin, UpdateMixin, SoftDeleteMixin


class Coupon(CreateMixin, UpdateMixin, SoftDeleteMixin):
    code = models.CharField(max_length=50, unique=True)
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    discount = models.IntegerField(help_text=_("درصد کد تخفیف"),
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.code

    def is_valid(self):
        now = timezone.now()
        return self.is_active and (self.valid_from <= now <= self.valid_to)

    class Meta:
        db_table = "discount_coupon"
