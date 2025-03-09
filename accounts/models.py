import datetime
from datetime import timedelta
from random import randint
from uuid import uuid4

from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.postgres.fields.array import ArrayField

from accounts.managers import UserManager, SoftManager
from accounts.validators import MobileRegexValidator, NationCodeRegexValidator, validate_upload_image_user
from api.v1.user.utils import ticket_validate_image, ticket_image_upload_url
from core.models import UpdateMixin, SoftDeleteMixin, CreateMixin
from utils.model_choices import Grade


class User(AbstractBaseUser, PermissionsMixin, UpdateMixin, SoftDeleteMixin, CreateMixin):
    mobile_phone = models.CharField(_("mobile phone"), max_length=15, unique=True)
    first_name = models.CharField(_("first name"), max_length=30, blank=True, null=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True, null=True)
    email = models.EmailField(_("email address"), unique=True, null=True, blank=True)
    is_staff = models.BooleanField(default=False, db_index=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    password = models.CharField(_("password"), max_length=128, blank=True, null=True)
    image = models.ImageField(_("عکس"), upload_to='user_image/%Y/%m/%d', blank=True, null=True,
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

    grade = models.CharField(_("grade"), max_length=8, choices=Grade.choices, blank=True, null=True)
    school = models.CharField(_("نام مدرسه"), max_length=30, blank=True, null=True)

    @property
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def is_student(self):
        return not self.is_coach

    def __str__(self):
        return self.mobile_phone

    @property
    def user_image_url(self):
        return self.image.url

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
        if timezone.now() > self.expired_date:
            return True
        return False

    @property
    def time_left_otp(self):
        return (self.expired_date - timezone.now()).seconds

    @property
    def create_otp_code(self):
        code = randint(1, 999999)
        return code

    def save(self, *args, **kwargs):
        self.code = self.create_otp_code
        self.expired_date = timezone.now() + timedelta(minutes=2)
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


class TicketRoom(CreateMixin, UpdateMixin, SoftDeleteMixin):
    """
    create ticket room
    """
    user = models.ForeignKey('accounts.User', on_delete=models.DO_NOTHING, related_name="ticker_room",
                             limit_choices_to={'is_active': True})
    title_room = models.CharField(max_length=50, help_text=_("عنوان چت روم تیکت"))
    is_active = models.BooleanField(default=True)
    is_close = models.BooleanField(default=False)

    def __str__(self):
        return self.title_room

    class Meta:
        db_table = "ticker_room"
        ordering = ("-created_at",)


class Ticket(CreateMixin, UpdateMixin, SoftDeleteMixin):
    """
    send ticket to admin
    """
    room = models.ForeignKey(TicketRoom, on_delete=models.DO_NOTHING, related_name="room")
    sender = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='sender',
                               limit_choices_to={"is_active": True})
    ticket_body = models.TextField(_("متن تیکت"))
    ticket_image = models.ImageField(upload_to=ticket_image_upload_url, validators=[ticket_validate_image],
                                     blank=True, null=True)
    is_publish = models.BooleanField(default=True)

    def __str__(self):
        return self.sender.mobile_phone

    class Meta:
        db_table = 'ticket'
        ordering = ['created_at']
        verbose_name = _("تیکت")
        verbose_name_plural = _("تیکت ها")


class TicketReply(CreateMixin, UpdateMixin, SoftDeleteMixin):
    ticket = models.ForeignKey(Ticket, on_delete=models.DO_NOTHING, related_name="reply")
    sender = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='reply_sender',
                               limit_choices_to={'is_staff': True})
    message = models.TextField()
    image = models.ImageField(upload_to=ticket_image_upload_url, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.sender.mobile_phone} {self.is_active}"

    class Meta:
        db_table = "ticket_reply"
        ordering = ['created_at']


class Coach(CreateMixin, UpdateMixin, SoftDeleteMixin):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, related_name='coach')
    coach_number = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.coach_number

    @property
    def get_coach_name(self):
        return self.user.get_full_name

    @property
    def get_coach_phone(self):
        return self.user.mobile_phone

    class Meta:
        db_table = 'coach'
        verbose_name = _("استاد")
        verbose_name_plural = _("اساتید")


class Student(CreateMixin, UpdateMixin, SoftDeleteMixin):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, related_name='student')
    student_number = models.CharField(max_length=11)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.student_number

    @property
    def student_name(self):
        return self.user.get_full_name

    @property
    def get_student_phone(self):
        return self.user.mobile_phone

    class Meta:
        db_table = 'student'
        ordering = ['-created_at']
        verbose_name = _("دانش اموز")
        verbose_name_plural = _("دانش اموزان")


class RequestLog(CreateMixin):
    path = models.CharField(max_length=255)
    method = models.CharField(max_length=10)
    meta_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.method} {self.path}"

    class Meta:
        db_table = 'request_log'


class BestStudent(CreateMixin, UpdateMixin, SoftDeleteMixin):
    student = models.CharField(max_length=50, help_text=_("نام دانش اموز"))
    student_image = models.ImageField(upload_to="best_student_image/%Y/%m/%d", null=True,
                                      validators=[validate_upload_image_user], help_text=_("حجم عکس اپلودی نباید بیش تر"
                                                                                           " از یک مگابایت باشد"))
    is_publish = models.BooleanField(default=True)
    description = models.CharField(max_length=500, null=True)
    attributes = ArrayField(models.CharField(max_length=20), null=True)

    class Meta:
        db_table = 'best_student'
        ordering = ['-created_at']
