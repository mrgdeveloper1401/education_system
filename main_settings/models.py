from django.db import models

from core.models import CreateMixin, UpdateMixin, SoftDeleteMixin

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
