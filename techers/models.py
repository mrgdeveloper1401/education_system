from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import SoftDeleteMixin, UpdateMixin, CreateMixin


class State(CreateMixin, UpdateMixin):
    state_name = models.CharField(_("state name"), max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.state_name

    class Meta:
        db_table = 'state'
        verbose_name = _("state")
        verbose_name_plural = _("states")


class City(CreateMixin, UpdateMixin):
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name='cities')
    city = models.CharField(_("city"), max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.state.state_name} {self.city}'

    class Meta:
        db_table = 'city'
        verbose_name = _("city")
        verbose_name_plural = _("cities")


class TeacherHome(CreateMixin, UpdateMixin):
    state = models.ForeignKey(State, on_delete=models.PROTECT, related_name='teacher_state_homes')
    city = models.ForeignKey(City, on_delete=models.PROTECT, related_name='teacher_city_homes')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.state.state_name} {self.city.city} {self.is_active}'

    class Meta:
        db_table = 'teacher_home'
        verbose_name = _("teacher_home")
        verbose_name_plural = _("teacher_homes")


class Teacher(CreateMixin, UpdateMixin, SoftDeleteMixin):
    teacher = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='techers')
    first_name = models.CharField(_("first_name"), max_length=30)
    last_name = models.CharField(_("last name"), max_length=30)
    email = models.EmailField(_("email address"), blank=True, null=True)
    teacher_home = models.ForeignKey(TeacherHome, on_delete=models.PROTECT, related_name='teachers')
    teacher_image = models.ForeignKey('images.Image', on_delete=models.PROTECT, related_name='teachers_image',
                                      blank=True, null=True)

    @property
    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        return f'{self.teacher.mobile_phone} {self.get_full_name}'

    class Meta:
        db_table = 'teacher'
        verbose_name = _("teacher")
        verbose_name_plural = _("teachers")


class TeacherNotification(CreateMixin, UpdateMixin, SoftDeleteMixin):
    teacher = models.ForeignKey('accounts.User', on_delete=models.PROTECT, related_name='teachers')
    title = models.CharField(_("title"), max_length=50)
    content = models.TextField(_("content"))
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.teacher.mobile_phone} {self.title}'

    class Meta:
        db_table = 'teacher_notification'
        verbose_name = _("teacher_notification")
        verbose_name_plural = _("teacher_notifications")
