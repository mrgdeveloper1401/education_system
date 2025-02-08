import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import ValidationError
from accounts.models import User
from core.models import CreateMixin, UpdateMixin, SoftDeleteMixin


class Subscription(CreateMixin, UpdateMixin, SoftDeleteMixin):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='subscriptions')
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        choices=[("active", _("فعال")), ("expired", _("منقضی شده")), ("nothing", _("هیچ")), ("waiting", _("انتظار"))],
        max_length=7,
        default="nothing"
    )

    def __str__(self):
        return f"{self.user.mobile_phone} - {self.start_date} to {self.end_date}"

    @property
    def number_of_day(self):
        if self.start_date == self.end_date:
            day = 'same day'
        else:
            day = (self.end_date - self.start_date).days
        return day

    def save(self, *args, **kwargs):
        if self.end_date < datetime.date.today():
            self.status = "expired"
        elif self.start_date > datetime.date.today():
            self.status = "waiting"
        else:
            self.status = "active"
        super().save(*args, **kwargs)

    def clean(self):
        subscription = Subscription.objects.filter(user=self.user).last()
        if self.end_date < self.start_date:
            raise ValidationError({"start_date": _("start date dont biggest end data")})
        if self.pk is None and subscription and (subscription.status == 'active' or subscription.status == "waiting"):
            raise ValidationError({"user": _("you have already subscription")})

    class Meta:
        db_table = 'subscription'
