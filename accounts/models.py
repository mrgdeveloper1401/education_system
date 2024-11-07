from builtins import set
from datetime import timedelta
from random import randint
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils.crypto import get_random_string
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _
from base64 import b64encode

from accounts.managers import UserManager
from accounts.validators import MobileRegexValidator, NationCodeRegexValidator, validate_upload_image_user
from core.models import UpdateMixin, SoftDeleteMixin, CreateMixin


class User(AbstractBaseUser, PermissionsMixin, UpdateMixin, SoftDeleteMixin, CreateMixin):
    mobile_phone = models.CharField(_("mobile phone"), max_length=11, unique=True,
                                    validators=[MobileRegexValidator()])
    first_name = models.CharField(_("first name"), max_length=30, blank=True, null=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True, null=True)
    email = models.EmailField(_("email address"), blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    password = models.CharField(_("password"), max_length=128, blank=True, null=True)
    image = models.ImageField(_("عکس کاربر"), upload_to='user_image/%Y/%m/%d', blank=True, null=True,
                              validators=[validate_upload_image_user])
    image_base64 = models.TextField(_("فورمت عکس base64"), blank=True, null=True)
    second_mobile_phone = models.CharField(_("شماره تماس دوم"), max_length=11, blank=True, null=True,
                                           validators=[MobileRegexValidator()])
    state = models.ForeignKey("State", on_delete=models.PROTECT, related_name='state', verbose_name=_("استان"),
                              blank=True, null=True)
    city = models.ForeignKey("City", on_delete=models.PROTECT, related_name='student_city', blank=True, null=True)
    nation_code = models.CharField(_("کد ملی"), max_length=10, validators=[NationCodeRegexValidator()],
                                   blank=True, null=True)
    address = models.TextField(_("ادرس"), blank=True, null=True)
    is_coach = models.BooleanField(_('به عنوان مربی'), default=False)
    is_student = models.BooleanField(_("به عنوان فراگیر"), default=False)
    birth_date = models.DateField(_("تاریخ نولد"), blank=True, null=True)

    class Gender(models.TextChoices):
        MALE = 'male', _("پسر")
        FEMALE = 'Female', _("دختر")

    gender = models.CharField(_("gender"), max_length=6, choices=Gender.choices, blank=True, null=True)

    class Grade(models.TextChoices):
        one = 'one', _("اول")
        two = 'two', _("دوم")
        three = 'three', _("سوم")
        four = 'four', _("چهارم")
        five = 'five', _("پنجم")
        six = 'six', _("ششم")
        seven = 'seven', _("هفتم")
        eight = 'eight', _("هشتم")
        nine = 'nine', _("نهم")
        ten = 'ten', _("دهم")
        eleven = 'eleven', _("یازدهم")
        twelfth = 'twelfth', _("دوازدهم")
        graduate = 'graduate', _("فارغ التحصیل")

    grade = models.CharField(_("grade"), max_length=8, choices=Grade.choices, blank=True, null=True)
    school = models.ForeignKey("School", on_delete=models.PROTECT, related_name='student_school',
                               verbose_name=_("مدرسه"), blank=True, null=True)

    def clean(self):
        if self.is_student and (self.is_staff or self.is_coach):
            raise ValidationError({"is_staff": _("کاربر فراگیر نمیتواند ادمین یا مربی باشد")})
        return super().clean()

    @property
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    USERNAME_FIELD = 'mobile_phone'
    REQUIRED_FIELDS = ['first_name', "last_name", "email"]
    objects = UserManager()

    class Meta:
        db_table = 'users'
        verbose_name = _('کاربر')
        verbose_name_plural = _('کاربران')
        constraints = [
            models.UniqueConstraint(fields=['email'], name='unique_emai_if_not_null', condition=Q(email__isnull=True)),
            models.UniqueConstraint(fields=['nation_code'], name='unique_nation_code_if_not_null',
                                    condition=Q(nation_code__isnull=True)),
            models.UniqueConstraint(fields=['second_mobile_phone'], name='unique_second_mobile_phone_if_not_null',
                                    condition=Q(second_mobile_phone__isnull=True)),
        ]

    @property
    def convert_image_to_base64(self):
        if self.image:
            encode_b64 = b64encode(self.image.read())
            return encode_b64.decode('utf-8')
        return None

    def save(self, *args, **kwargs):
        if not self.password:
            self.password = self.set_password(get_random_string(10))
        self.image_base64 = self.convert_image_to_base64
        return super().save()


class Otp(CreateMixin):
    mobile_phone = models.CharField(_("mobile phone"), max_length=11, validators=[MobileRegexValidator()])
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

    class Meta:
        db_table = 'otp_code'
        verbose_name = _("کد")
        verbose_name_plural = _("کد ها")


class State(CreateMixin, UpdateMixin, SoftDeleteMixin):
    state_name = models.CharField(_("استان"), max_length=30, unique=True)

    def __str__(self):
        return self.state_name

    class Meta:
        db_table = "state"
        verbose_name = _("استان")
        verbose_name_plural = _("استان ها")


class City(CreateMixin, UpdateMixin, SoftDeleteMixin):
    state_name = models.ForeignKey(State, on_delete=models.PROTECT, related_name="city", verbose_name=_("استان"))
    city = models.CharField(_("شهر"), max_length=30)

    def __str__(self):
        return self.city

    class Meta:
        db_table = "city"
        verbose_name = _("شهر")
        verbose_name_plural = _("شهر ها")
        unique_together = [('state_name', "city")]


class School(CreateMixin, UpdateMixin, SoftDeleteMixin):
    school_name = models.CharField(_("نام مدرسه"), max_length=30)

    def __str__(self):
        return self.school_name

    class Meta:
        db_table = 'school'
        verbose_name = _("مدرسه")
        verbose_name_plural = _("مدرسه ها")
