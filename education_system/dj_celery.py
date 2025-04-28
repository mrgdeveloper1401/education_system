from celery import Celery
import os
from education_system.base import DEBUG

os.environ.setdefault(
    'DJANGO_SETTINGS_MODULE',
    "education_system.envs.development" if DEBUG else "education_system.envs.production"
)

app = Celery()
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()