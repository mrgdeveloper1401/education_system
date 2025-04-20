from rest_framework.exceptions import ValidationError


def max_upload_image_validator(value):
    max_size = 1
    image_size = value.size
    upload_image_size = value.size / 1024 / 1024

    if image_size > max_size * 1024 * 1024:
        raise ValidationError({"message": f"max size upload image {max_size} MB you image size is "
                                          f"{upload_image_size:.2f} MB"})
    return value
