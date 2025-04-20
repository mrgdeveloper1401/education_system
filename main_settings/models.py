from django.db import models
from django.core import exceptions

from core.models import CreateMixin, UpdateMixin, SoftDeleteMixin
from utils.validators import file_upload_validator


# TODO when clean migration, i'm remove argument blank in field banner_type
class Banner(CreateMixin, UpdateMixin, SoftDeleteMixin):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='banners/%Y/%m/%d')
    is_publish = models.BooleanField(default=True)
    banner_type = models.CharField(
        choices=(("coach", "coach"), ("student", "student"), ("public", "public")),
        max_length=7,
        blank=True,
        help_text="Banner type",
    )

    class Meta:
        db_table = 'banner'
        ordering = ('-created_at',)


class HeaderSite(CreateMixin, UpdateMixin, SoftDeleteMixin):
    header_title = models.CharField(max_length=50, help_text="عنوان هدر", blank=True, null=True)
    image = models.ImageField(upload_to="header_title/%Y/%m/%d", validators=[file_upload_validator],
                              blank=True, null=True)
    is_publish = models.BooleanField(default=True)

    def clean(self):
        if not self.header_title and not self.image:
            raise exceptions.ValidationError({"header_title": "header title and image At least one of thise should be"})

    class Meta:
        db_table = "header_site"
