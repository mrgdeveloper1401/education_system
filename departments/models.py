from django.db import models
from django.utils.translation import gettext_lazy as _

from core.models import UpdateMixin, CreateMixin, SoftDeleteMixin


# Create your models here.


class Department(UpdateMixin, CreateMixin, SoftDeleteMixin):
    user = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name='user_departments',
                             limit_choices_to={"is_active": True, "is_staff": True})
    department_name = models.CharField(_("نام دپارتمان"), max_length=30, unique=True)

    def __str__(self):
        return f'{self.user.get_full_name} {self.department_name}'

    class Meta:
        db_table = 'department'
        verbose_name = _("دپارتمان")
        verbose_name_plural = _("دپارتمان ها")
        unique_together = ("user", "department_name",)
