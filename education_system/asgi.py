"""
ASGI config for education_system project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from decouple import config

from django.core.asgi import get_asgi_application

debug_mode = config('DEBUG', cast=bool, default=False)
if debug_mode:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "education_system.envs.development")
else:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "education_system.envs.production")

application = get_asgi_application()
