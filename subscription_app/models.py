import datetime

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import ValidationError, MinValueValidator
from accounts.models import User
from core.models import CreateMixin, UpdateMixin, SoftDeleteMixin


class Subscription(CreateMixin, UpdateMixin, SoftDeleteMixin):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='subscriptions')
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    status = models.CharField(
        choices=[("active", _("فعال")), ("expired", _("منقضی شده")), ("nothing", _("هیچ")), ("waiting", _("انتظار")),
                 ("delete", _("حذف شده"))],
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
        if self.is_active is False:
            self.status = "delete"
        super().save(*args, **kwargs)

    def clean(self):
        subscription = Subscription.objects.filter(user__mobile_phone=self.user, is_active=True).last()
        count_sub = Subscription.objects.filter(user__mobile_phone=self.user, is_active=True).count()
        if self.end_date < self.start_date:
            raise ValidationError({"start_date": _("start date dont biggest end data")})
        if self.pk is None and subscription and (subscription.status == 'active' or subscription.status == "waiting"):
            raise ValidationError({"user": _("you have already active subscription")})
        # if count_sub >= 1:
        #     raise ValidationError({"user": _("you have already active subscription")})

    class Meta:
        db_table = 'subscription'


class Plan(CreateMixin, UpdateMixin, SoftDeleteMixin):
    plan_title = models.CharField(help_text=_("عنوان پلن"))
    number_of_days = models.PositiveSmallIntegerField()
    price = models.FloatField(validators=[MinValueValidator(0)])
    is_free = models.BooleanField(default=False)
    description = models.TextField(help_text=_("توضیحی در مورد پلن"))
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.plan_title

    def clean(self):
        if self.is_free and self.price > 0:
            raise ValidationError({"is_free", _("dont create plan when is_free and not free")})

    class Meta:
        db_table = 'plan'


class AccessCourse(CreateMixin, UpdateMixin, SoftDeleteMixin):
    user = models.ForeignKey("accounts.User", on_delete=models.DO_NOTHING, related_name='access_user')
    course = models.ForeignKey('course.Course', on_delete=models.DO_NOTHING, related_name='access_course')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.mobile_phone} {self.course.course_name}'

    class Meta:
        db_table = 'access_course'
