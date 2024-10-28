from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class CreateMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class UpdateMixin(models.Model):
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    deleted_at = models.DateTimeField(blank=True, null=True, editable=False)
    is_deleted = models.BooleanField(default=False, editable=False)

    def delete(self, *args, **kwargs):
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.save(*args, **kwargs)

    class Meta:
        abstract = True
