from education_system.settings import *

SECRET_KEY = config('SECRET_KEY', cast=str)

DEBUG = config('DEBUG', default=False, cast=bool)

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": 'education_system',
        'USER': "postgres",
        "PASSWORD": "postgres",
        'HOST': "localhost",
        "PORT": 5432,
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
