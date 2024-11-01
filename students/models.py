from django.db import models
from django.utils.translation import gettext_lazy as _

from accounts.validators import MobileRegexValidator, NationCodeRegexValidator
from core.models import CreateMixin, UpdateMixin, SoftDeleteMixin


class State(CreateMixin, SoftDeleteMixin, UpdateMixin):
    state_name = models.CharField(_("استان"), max_length=30, unique=True)

    def __str__(self):
        return self.state_name

    class Meta:
        db_table = 'state'
        verbose_name = _("استان")
        verbose_name_plural = _("استان ها")


class City(CreateMixin, SoftDeleteMixin, UpdateMixin):
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name='city')
    city_name = models.CharField(_("شهر"), max_length=30, unique=True)

    def __str__(self):
        return f'{self.state.state_name} {self.city_name}'

    class Meta:
        db_table = 'city'
        verbose_name = _("شهر")
        verbose_name_plural = _("شهر ها")


class Student(CreateMixin, UpdateMixin, SoftDeleteMixin):
    student = models.OneToOneField('accounts.User', related_name='student', on_delete=models.PROTECT)
    image = models.ForeignKey('images.Image', related_name='student_image', on_delete=models.PROTECT, blank=True,
                              null=True)
    second_mobile_phone = models.CharField(_("شماره تماس دوم"), max_length=11, blank=True, null=True,
                                           validators=[MobileRegexValidator()])
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='student_city')
    nation_code = models.CharField(_("کد ملی"), max_length=10, unique=True, validators=[NationCodeRegexValidator()])
    address = models.TextField(_("ادرس"), blank=True, null=True)
    is_coach = models.BooleanField(_('به عنوان مربی'), default=False)
    is_student = models.BooleanField(_("به عنوان فراگیر"), default=False)

    class Gender(models.TextChoices):
        MALE = 'M', _("پسر")
        FEMALE = 'F', _("دختر")

    gender = models.CharField(_("gender"), max_length=1, choices=Gender.choices)

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

    grade = models.CharField(_("grade"), max_length=8, choices=Grade.choices)

    @property
    def get_full_name(self):
        return f'{self.student.first_name} {self.student.last_name} {self.student.mobile_phone}'

    class Meta:
        db_table = 'student'
        verbose_name = _('student')
        verbose_name_plural = _('students')


class StudentNotification(CreateMixin, SoftDeleteMixin):
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name='student_notification')
    is_active = models.BooleanField(default=True)
    message = models.TextField(_("message"))
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.student.get_full_name

    class Meta:
        db_table = 'student_notification'
        verbose_name = _('student notification')
        verbose_name_plural = _('student notifications')
