from django.db import models
from django.utils.translation import gettext_lazy as _


class ProgresChoices(models.TextChoices):
    not_started = "not_started", _("Not Started")
    finished = "finished", _("Finished")
    in_progress = "in_progress", _("In Progress")


class SectionFileType(models.TextChoices):
    main = "main", _("تمرین اصلی")
    more_then = "more", _("تمرین اضافی")
    gold = "gold", _("طلایی")


class StudentStatusChoices(models.TextChoices):
    present = "present", _("حاضر")
    absent = "absent", _("غایب")
    late_attendance = "late_attendance", _("حضور با تاخیر")
    inactivity = "inactivity", _("عدم فعالیت")
