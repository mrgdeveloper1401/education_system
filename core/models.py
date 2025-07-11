from django.db import models
from django.utils import timezone

from core.managers import PublishManager


class CreateMixin(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        abstract = True


class UpdateMixin(models.Model):
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteMixin(models.Model):
    deleted_at = models.DateTimeField(null=True, editable=False)
    is_deleted = models.BooleanField(editable=False, null=True)

    objects = PublishManager()

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.is_deleted = True
        self.save()

    class Meta:
        abstract = True


class SitemapEntry(CreateMixin, SoftDeleteMixin):
    slug_text = models.TextField()
    last_modified = models.CharField(blank=True)
    changefreq = models.CharField(
        max_length=255,
    )
    priority = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.5,
        help_text='A value between 0.00 and 1.00'
    )

    class Meta:
        db_table = "site_map"
