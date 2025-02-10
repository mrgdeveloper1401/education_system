from django.db import models
from django.db.models import Q
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return super().update(is_deleted=True, deleted_at=timezone.now())


class PublishManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(
            Q(is_deleted=False) | Q(is_deleted__isnull=True)
        )
