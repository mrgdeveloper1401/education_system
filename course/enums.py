from django.db import models
from django.utils.translation import gettext_lazy as _


class ProgresChoices(models.TextChoices):
    not_started = "not_started", _("Not Started")
    finished = "finished", _("Finished")
    in_progress = "in_progress", _("In Progress")
