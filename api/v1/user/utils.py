from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def ticket_image_upload_url(instance, filename):
    user = instance.sender
    return f"ticket/%Y/%m/%d/{user}/"


def ticket_validate_image(value):
    max_size = 1
    image_size = value.size
    if image_size > max_size * 1024 * 1024:
        raise ValidationError({"message": _("max image size is 1 MG")})
    return value
