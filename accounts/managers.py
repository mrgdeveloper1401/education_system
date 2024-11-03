from django.contrib.auth.models import UserManager as BaseUserManager
from django.utils.crypto import get_random_string


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
