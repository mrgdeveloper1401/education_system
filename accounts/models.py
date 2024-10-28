from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.validators import MobileRegexValidator
from core.models import UpdateMixin, SoftDeleteMixin, CreateMixin


class User(AbstractBaseUser, PermissionsMixin, UpdateMixin, SoftDeleteMixin):
    mobile_phone = models.CharField(_("mobile phone"), max_length=11, unique=True,
                                    validators=[MobileRegexValidator()])
    email = models.EmailField(_("email address"), blank=True, null=True)
    is_student = models.BooleanField(default=False)
    is_teacher = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'mobile_phone'

    class Meta:
        db_table = 'users'
        verbose_name = _('user')
        verbose_name_plural = _('users')
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_email'),
        ]
