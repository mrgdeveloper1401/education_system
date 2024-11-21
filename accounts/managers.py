from django.contrib.auth.models import UserManager as BaseUserManager
from django.db.models import QuerySet, Manager, Q
from django.utils.timezone import now


class SoftQuerySet(QuerySet):
    def delete(self):
        return self.update(is_deleted=True, deleted_at=now(), is_active=False)


class UserManager(BaseUserManager):
    def create_user(self, mobile_phone, password=None, **extra_fields):
        if not mobile_phone:
            raise ValueError('Mobile phone is required')
        user = self.model(mobile_phone=mobile_phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, mobile_phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        return self.create_user(mobile_phone, password, **extra_fields)

    def get_queryset(self):
        return SoftQuerySet(self.model, using=self._db).filter(Q(is_deleted=False) | Q(is_deleted=None))


class SoftManager(Manager):
    def get_queryset(self):
        return SoftQuerySet(self.model, using=self._db).filter(is_deleted=True)
