from django.core.validators import ValidationError


def file_upload_validator(value):
    max_size = 1 * 1024 * 1024 * 1024
    if value.size > max_size:
        raise ValidationError(f"{value.size} is biggest {max_size}")
    return value
