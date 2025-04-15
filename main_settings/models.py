from django.db import models

from core.models import CreateMixin, UpdateMixin, SoftDeleteMixin


class Banner(CreateMixin, UpdateMixin, SoftDeleteMixin):
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='banners/%Y/%m/%d')
    is_publish = models.BooleanField(default=True)

    class Meta:
        db_table = 'banner'
        ordering = ('-created_at',)
