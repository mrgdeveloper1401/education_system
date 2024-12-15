from education_system.base import *

SECRET_KEY = config('DEVELOP_SECRET_KEY', cast=str)


DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": 'practicedb',
        'USER': "postgres",
        "PASSWORD": "postgres.2024",
        'HOST': "localhost",
        "PORT": 5498,
    }
}

INSTALLED_APPS += [
    "debug_toolbar",
]

MIDDLEWARE += [
    "debug_toolbar.middleware.DebugToolbarMiddleware",
]

INTERNAL_IPS = [
    # ...
    "127.0.0.1",
    # ...
]

SIMPLE_JWT['SIGNING_KEY'] = SECRET_KEY
