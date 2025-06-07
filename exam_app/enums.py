from django.db import models
from django.utils.translation import gettext_lazy as _


class QuestionType(models.TextChoices):
    MULTIPLE_CHOICE = 'MC', _('چند گزینه‌ای')
    DESCRIPTIVE = 'DE', _('تشریحی')
