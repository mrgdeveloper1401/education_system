from datetime import timedelta
from random import randint
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from accounts.managers import UserManager, SoftManager
from accounts.validators import MobileRegexValidator, NationCodeRegexValidator, validate_upload_image_user
from core.models import UpdateMixin, SoftDeleteMixin, CreateMixin


class User(AbstractBaseUser, PermissionsMixin, UpdateMixin, SoftDeleteMixin, CreateMixin):
    mobile_phone = models.CharField(_("mobile phone"), max_length=11, unique=True,
                                    validators=[MobileRegexValidator()])
    first_name = models.CharField(_("first name"), max_length=30, blank=True, null=True,
                                  db_index=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True, null=True,
                                 db_index=True)
    email = models.EmailField(_("email address"), unique=True, null=True,
                              db_index=True)
    is_staff = models.BooleanField(default=False, db_index=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    password = models.CharField(_("password"), max_length=128, blank=True, null=True)
    image = models.ImageField(_("عکس کاربر"), upload_to='user_image/%Y/%m/%d', blank=True, null=True,
                              validators=[validate_upload_image_user])
    second_mobile_phone = models.CharField(_("شماره تماس دوم"), max_length=11, blank=True, null=True,
                                           validators=[MobileRegexValidator()])
    state = models.ForeignKey("State", on_delete=models.PROTECT, related_name='state', verbose_name=_("استان"),
                              blank=True, null=True)
    city = models.ForeignKey("City", on_delete=models.PROTECT, related_name='student_city', blank=True, null=True)
    nation_code = models.CharField(_("کد ملی"), max_length=10, unique=True, null=True,
                                   validators=[NationCodeRegexValidator()])
    address = models.TextField(_("ادرس"), blank=True, null=True)
    is_coach = models.BooleanField(_('به عنوان مربی'), default=False)
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
    school = models.CharField(_("نام مدرسه"), max_length=30, blank=True, null=True)

    @property
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def deactivate_user(self):
        self.is_active = False
        self.is_verified = False
        self.is_deleted = True
        self.deleted_at = now()
        self.is_staff = False
        self.save()

    USERNAME_FIELD = 'mobile_phone'
    REQUIRED_FIELDS = ['first_name', "last_name", "email"]

    objects = UserManager()

    class Meta:
        db_table = 'users'
        verbose_name = _('کاربر')
        verbose_name_plural = _('کاربران')
        ordering = ("-created_at",)


class RecycleUser(User):
    objects = SoftManager()

    class Meta:
        proxy = True
        verbose_name = _("کاربر پاک شده")
        verbose_name_plural = _("کاربران پاک شده")


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
        ordering = ('created_at',)


class State(models.Model):
    state_name = models.CharField(_("استان"), max_length=30, unique=True)

    def __str__(self):
        return self.state_name

    class Meta:
        db_table = "state"
        verbose_name = _("استان")
        verbose_name_plural = _("استان ها")


class City(models.Model):
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name="cites", verbose_name=_("استان"),
                              related_query_name='city')
    city = models.CharField(_("شهر"), max_length=40, db_index=True)

    def __str__(self):
        return self.city

    class Meta:
        db_table = "city"
        verbose_name = _("شهر")
        verbose_name_plural = _("شهر ها")
        unique_together = [('state', "city")]


class Ticket(CreateMixin, UpdateMixin, SoftDeleteMixin):
    coach = models.ForeignKey(User, on_delete=models.PROTECT, related_name='coach_ticker',
                              limit_choices_to={"is_active": True, "is_coach": True, "is_deleted": False},
                              verbose_name=_("مربی"))
    department = models.ForeignKey("departments.Department", on_delete=models.PROTECT, related_name='admin_ticket',
                                   limit_choices_to={"user__is_active": True, "user__is_staff": True,
                                                     "user__is_deleted": False},
                                   verbose_name=_("کاربر ادمین"))
    ticker_body = models.TextField(_("متن تیکت"))
    subject_ticket = models.CharField(_("عنوان تیکت"), max_length=255)
    is_publish = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.coach.get_full_name} {self.department.department_name}'

    class Meta:
        db_table = 'ticket'
        verbose_name = _("تیکت")
        verbose_name_plural = _("تیکت ها")


class UserLogins(CreateMixin):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='logins')
    success_login = models.PositiveIntegerField(default=0)
    failed_login = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f'{self.user} {self.success_login} {self.failed_login}'

    class Meta:
        db_table = 'user_logins'
        verbose_name = _("لاگین های کاربر")
        verbose_name_plural = _("لاگین های کاربران")


class UserDevice(CreateMixin):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='device')
    is_linux = models.BooleanField(default=False)
    is_windows = models.BooleanField(default=False)
    is_max = models.BooleanField(default=False)
    is_iphone = models.BooleanField(default=False)
    is_android = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.get_full_name} {self.created_at}'

    class Meta:
        db_table = 'user_device'
        verbose_name = _("دستگاه های کاربر")
        verbose_name_plural = _("دستگاه های کاربران")


class UserIp(CreateMixin):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ip')
    user_ip = models.GenericIPAddressField()

    def __str__(self):
        return f'{self.user.mobile_phone} {self.user_ip}'

    class Meta:
        db_table = 'user_ip'
        verbose_name = _('ای پی کاربر')
        verbose_name_plural = _("ای پی کاربران")
