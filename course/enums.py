from django.db import models
from django.utils.translation import gettext_lazy as _


class ProgresChoices(models.TextChoices):
    not_started = "not_started", _("Not Started")
    finished = "finished", _("Finished")
    in_progress = "in_progress", _("In Progress")


class SectionFileType(models.TextChoices):
    main = "main", _("تمرین اصلی")
    more_then = "more", _("تمرین اضافی")
    # gold = "gold", _("طلایی")


class StudentStatusChoices(models.TextChoices):
    present = "present", _("حاضر")
    activity = "activity", _("حضور فعال")
    absent = "absent", _("غایب")
    late_attendance = "late_attendance", _("حضور با تاخیر")
    inactivity = "inactivity", _("عدم فعالیت")
    nothing = "nothing", _("خالی")


class RateChoices(models.TextChoices):
    one = "1", _("1")
    two = "2", _("2")
    three = "3", _("3")
    four = "4", _("4")
    five = "5", _("5")
    six = "6", _("6")
    seven = "7", _("7")
    eight = "8", _("8")
    nine = "9", _("9")
    ten = "10", _("10")


class SendFileChoices(models.TextChoices):
    rejected = "rejected", _("رد شده")
    accept_to_wait = "accept_to_wait", _("در انتظا تایید")
    accepted = "accepted", _("تایید شده")


class CallStatusChoices(models.TextChoices):
    successful = "successful", _("موفق")
    un_successful = "un_successful", _("ناموفق")
    nothing = "nothing", _("چیزی ثبت نشده هست")


class NumberOfDaysChoices(models.TextChoices):
    one = "1", _("یک ماهه")
    two = "2", _("دو ماهه")
    three = "3", _("سه ماهه")
    four = "4", _("چهار ماهه")
    five = "5", _("پنج ماهه")
    six = "6", _("شش ماه")
    seven = "7", _("هفت ماه")
    eight = "8", _("هشت ماه")
    nine = "9", _("نه ماهه")
    ten = "10", _("ده ماهه")
    eleven = "11", _("یازده ماهه")
    two_eleven = "12", _("دوازده ماهه")
