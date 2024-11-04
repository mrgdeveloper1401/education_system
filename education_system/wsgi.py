"""
WSGI config for education_system project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/wsgi/
"""

import os
from decouple import config

from django.core.wsgi import get_wsgi_application


debug_mode = config('DEBUG', cast=bool, default=False)
if debug_mode:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "education_system.envs.development")
if not debug_mode:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "education_system.envs.production")

application = get_wsgi_application()
