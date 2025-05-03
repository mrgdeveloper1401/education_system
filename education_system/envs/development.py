from education_system.base import *

SECRET_KEY = config('DEVELOP_SECRET_KEY', cast=str)

CORS_ALLOW_ALL_ORIGINS = True

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql_psycopg2",
        "NAME": 'educationdb',
        'USER': "postgres",
        "PASSWORD": "postgres",
        'HOST': "localhost",
        "PORT": 5433,
    },
    # "chat_db": {
    #     "ENGINE": "djongo",
    #     "NAME": 'mongo_education_system',
    #     "ENFORCE_SCHEMA": False,
    #     "CLIENT": {
    #         "host": "localhost",
    #     }
    # }
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

JWT_SECRET = ""
JWT_AUDIENCE = ""
JWT_ISSUER = ""

# Static files (CSS, JavaScript, Images)
STATIC_URL = config('STATIC_URL', cast=str)
STATIC_ROOT = BASE_DIR / config("STATIC_ROOT", cast=str)

MEDIA_URL = config("MEDIA_URL", cast=str)
MEDIA_ROOT = config("MEDIA_ROOT", cast=str)

# Celery settings
CELERY_BROKER_URL = "redis://localhost:6380"
CELERY_RESULT_BACKEND = "redis://localhost:6380"