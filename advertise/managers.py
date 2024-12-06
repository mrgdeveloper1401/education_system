from django.db import models
from django.utils import timezone


class PublishSlotManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(date__gte=timezone.now())
