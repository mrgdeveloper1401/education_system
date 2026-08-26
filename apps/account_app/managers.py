from django.contrib.auth.models import UserManager as BaseUserManager
from django.db.models import QuerySet, Manager, Q
from django.utils.timezone import now


class SoftQuerySet(QuerySet):
    def delete(self):
        return self.update(is_deleted=True, deleted_at=now())


class SoftManager(Manager):
    def get_queryset(self):
        return SoftQuerySet(self.model, using=self._db).filter(is_deleted=True)
