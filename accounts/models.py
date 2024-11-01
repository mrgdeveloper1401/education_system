from datetime import timedelta
from random import randint
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from accounts.managers import UserManager
from accounts.validators import MobileRegexValidator
from core.models import UpdateMixin, SoftDeleteMixin, CreateMixin


class User(AbstractBaseUser, PermissionsMixin, UpdateMixin, SoftDeleteMixin, CreateMixin):
    mobile_phone = models.CharField(_("mobile phone"), max_length=11, unique=True,
                                    validators=[MobileRegexValidator()])
    first_name = models.CharField(_("first name"), max_length=30, blank=True, null=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True, null=True)
    email = models.EmailField(_("email address"), blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    USERNAME_FIELD = 'mobile_phone'
    REQUIRED_FIELDS = ['first_name', "last_name"]
    objects = UserManager()

    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_email'),
        ]


class Otp(CreateMixin):
    mobile_phone = models.CharField(_("mobile phone"), max_length=11 ,validators=[MobileRegexValidator()])
    code = models.CharField(_("code"), max_length=6, blank=True)
    expired_date = models.DateTimeField(_("expired date"), blank=True)

    @property
    def is_expired(self):
        if now() > self.expired_date:
            return True
        return False

    @property
    def create_otp_code(self):
        code = randint(1, 999999)
        return code

    def save(self, *args, **kwargs):
        self.code = self.create_otp_code
        self.expired_date = now() + timedelta(minutes=2)
        return super().save(*args, **kwargs)
