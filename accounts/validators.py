from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class MobileRegexValidator(RegexValidator):
    regex = r'^09\d{9}'
    message = _("با 09 شروع شود و یازده رقمی باشد")


# def nation_code_validator(value):
#     if not isinstance(value, int):
#         raise ValidationError(_("شماره ملی باید به صورت عدد باشد"))
#     return value
