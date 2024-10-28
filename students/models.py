from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import CreateMixin, UpdateMixin, SoftDeleteMixin


class Student(CreateMixin, UpdateMixin, SoftDeleteMixin):
    student = models.OneToOneField('accounts.User', related_name='student', on_delete=models.PROTECT)
    first_name = models.CharField(_("first name"), max_length=30, blank=True, null=True)
    last_name = models.CharField(_("last name"), max_length=30, blank=True, null=True)
    image = models.ForeignKey('images.Image', related_name='student_image', on_delete=models.PROTECT, blank=True,
                              null=True)

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
        return f'{self.first_name} {self.last_name}'

    class Meta:
        db_table = 'staudent'
        verbose_name = _('staudent')
        verbose_name_plural = _('staudents')


class StudentNotification(CreateMixin, SoftDeleteMixin):
    student = models.ForeignKey(Student, on_delete=models.PROTECT, related_name='student_notification')
    is_active = models.BooleanField(default=True)
    message = models.TextField(_("message"))
    url = models.URLField(_("url"))
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return self.student.get_full_name

    class Meta:
        db_table = 'student_notification'
        verbose_name = _('student notification')
        verbose_name_plural = _('student notifications')
