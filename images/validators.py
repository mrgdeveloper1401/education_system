from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_image_size(value):
    max_size = 1
    if value.size > max_size * 1024 * 1024:
        raise ValidationError(_("حداکثر حجم عکس 1 مگابایت باشد"))
    return value
