import io
import uuid
from pathlib import Path

from PIL.ImageOps import exif_transpose
from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser
from django.core.files.base import ContentFile
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields.array import ArrayField
from treebeard.mp_tree import MP_Node
from PIL import Image as PILImage

from apps.account_app.managers import UserManager
from apps.account_app.validators import MobileRegexValidator, NationCodeRegexValidator, validate_upload_image_user
from apps.core_app.models import UpdateMixin, SoftDeleteMixin, CreateMixin, State, City


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


class User(AbstractBaseUser, PermissionsMixin, UpdateMixin, SoftDeleteMixin, CreateMixin):
    mobile_phone = models.CharField(_("mobile phone"), max_length=15, unique=True)
    first_name = models.CharField(_("first name"), max_length=30, blank=True, null=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True, null=True)
    email = models.EmailField(_("email address"), null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    password = models.CharField(_("password"), max_length=128, blank=True, null=True)
    image = models.ImageField(_("عکس"), upload_to='user_image/%Y/%m/%d', blank=True, null=True,
                              validators=[validate_upload_image_user])
    second_mobile_phone = models.CharField(_("شماره تماس دوم"), max_length=11, blank=True, null=True,
                                           validators=[MobileRegexValidator()])
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name='state', verbose_name=_("استان"),
                              blank=True, null=True)
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='student_city', blank=True, null=True)
    nation_code = models.CharField(_("کد ملی"), max_length=10, null=True, blank=True,
                                   validators=[NationCodeRegexValidator()])
    address = models.TextField(_("ادرس"), blank=True, null=True)
    is_coach = models.BooleanField(_('به عنوان مربی'), default=False)
    birth_date = models.DateField(_("تاریخ نولد"), blank=True, null=True)
    bio = models.CharField(max_length=500, blank=True, null=True)

    class Gender(models.TextChoices):
        MALE = 'male', _("پسر")
        FEMALE = 'Female', _("دختر")

    gender = models.CharField(_("gender"), max_length=6, choices=Gender.choices, blank=True, null=True)

    grade = models.CharField(_("grade"), max_length=8, choices=Grade.choices, blank=True, null=True)
    school = models.CharField(_("نام مدرسه"), max_length=30, blank=True, null=True)

    @property
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}' if self.first_name and self.last_name else None

    @property
    def is_student(self):
        return not self.is_coach

    def __str__(self):
        return self.mobile_phone

    @property
    def user_image_url(self):
        return self.image.url

    USERNAME_FIELD = 'mobile_phone'
    REQUIRED_FIELDS = ('first_name', "last_name", "email")

    objects = UserManager()

    class Meta:
        ordering = ("id",)
        db_table = 'users'
        verbose_name = _('کاربر')
        verbose_name_plural = _('کاربران')


class TicketRoom(CreateMixin, UpdateMixin, SoftDeleteMixin):
    """
    create ticket room
    """
    user = models.ForeignKey('User', on_delete=models.DO_NOTHING, related_name="ticker_room")
    title_room = models.CharField(max_length=50, help_text=_("عنوان چت روم تیکت"))
    subject_room = models.CharField(max_length=50, help_text=_("موضوع تیکت"))
    is_active = models.BooleanField(default=True)
    is_close = models.BooleanField(default=False)

    class Meta:
        db_table = "ticker_room"
        verbose_name = _("اتاق تیکت")
        verbose_name_plural = _("اتاق های تیکت")


class Ticket(MP_Node, CreateMixin, UpdateMixin, SoftDeleteMixin):
    """
    send ticket to admin
    """
    room = models.ForeignKey(TicketRoom, on_delete=models.DO_NOTHING, related_name="room")
    sender = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='sender')
    reply = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="ticket_reply", blank=True, null=True)
    ticket_body = models.TextField(_("متن تیکت"))
    ticket_file = models.FileField(upload_to="ticket/%Y/%m/%d", blank=True, null=True)
    is_publish = models.BooleanField(default=True)

    class Meta:
        db_table = 'ticket'
        verbose_name = _("تیکت")
        verbose_name_plural = _("تیکت ها")


class Coach(CreateMixin, UpdateMixin, SoftDeleteMixin):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, related_name='coach')
    coach_number = models.CharField(max_length=15, blank=True)
    is_active = models.BooleanField(default=True)

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
    referral_code = models.CharField(max_length=30, blank=True, db_index=True)
    is_active = models.BooleanField(default=True)

    @property
    def student_name(self):
        return self.user.get_full_name

    @property
    def get_student_phone(self):
        return self.user.mobile_phone

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = uuid.uuid4().hex[:30]
            while Student.objects.filter(referral_code=self.referral_code).exists():
                self.referral_code = uuid.uuid4().hex[:30]
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'student'
        verbose_name = _("دانش اموز")
        verbose_name_plural = _("دانش اموزان")


class BestStudent(CreateMixin, UpdateMixin, SoftDeleteMixin):
    student = models.CharField(max_length=50, help_text=_("نام دانش اموز"))
    student_image = models.ImageField(
        upload_to="best_student_image/%Y/%m/%d",
        null=True,
        validators=[validate_upload_image_user],
        help_text=_("حجم عکس اپلودی نباید بیش تر" " از یک مگابایت باشد")
    )
    is_publish = models.BooleanField(default=True)
    description = models.CharField(max_length=500, null=True)
    attributes = ArrayField(models.CharField(max_length=100), null=True)

    @property
    def _is_webp(self) -> bool:
        return Path(self.student_image.name).suffix.lower() == ".webp"

    def conv_img_into_webp(self, quality = 100):
        if not self.student_image or self._is_webp:
            return

        buffer = io.BytesIO()
        with PILImage.open(self.student_image) as img:
            if getattr(img, "is_animated", False):
                # گیف متحرک: باید همه فریم‌ها ذخیره بشن
                img.save(buffer, format="WEBP", quality=quality, save_all=True)
            else:
                img = exif_transpose(img)
                # حفظ کانال آلفا برای png و مشابهش
                mode = "RGBA" if img.mode in ("RGBA", "LA", "P") else "RGB"
                img.convert(mode).save(buffer, format="WEBP", quality=quality)
        new_name = f"{Path(self.student_image.name).stem}.webp"
        self.student_image.save(new_name, ContentFile(buffer.getvalue()), save=False)

    def save(self, *args, **kwargs):
        self.conv_img_into_webp()
        return super().save(*args, **kwargs)

    class Meta:
        db_table = 'best_student'
        verbose_name = _("دانش اموز برتر")
        verbose_name_plural = _("دانش اموزان برتر")


class PrivateNotification(CreateMixin, UpdateMixin, SoftDeleteMixin):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="notifications")
    title = models.CharField(max_length=255)
    body = models.TextField()
    char_link = models.CharField(blank=True, max_length=100, null=True, help_text="link for redirect")
    notification_type = models.CharField(max_length=30, blank=True, null=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ("id",)
        db_table = 'private_notification'
        verbose_name = _("نوتیفیکیشن کاربر")
        verbose_name_plural = _("نوتیفیکیشن های کاربر")


class Invitation(CreateMixin, SoftDeleteMixin):
    # student send referral code
    from_student = models.ForeignKey(Student, on_delete=models.DO_NOTHING, related_name="from_invasion",
                                     verbose_name=_("از دانش اموز"))
    # student enter referral code
    to_student = models.ForeignKey(Student, on_delete=models.DO_NOTHING, related_name="to_invasion",
                                   verbose_name=_("به داشن اموز"))

    class Meta:
        db_table = 'invitation'
        verbose_name = _("دعوت")
        verbose_name_plural = _("دعوت ها")
