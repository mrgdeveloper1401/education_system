from education_system.base import *

SECRET_KEY = config('DEVELOP_SECRET_KEY', cast=str)

CORS_ALLOW_ALL_ORIGINS = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
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

# ADMINS = [
#     ("mohammad goodarzi", "mysum325g@gmail.com")
# ]

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config("EMAIL_HOST", cast=str)
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = config("EMAIL_HOST_USER", cast=str)
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", cast=str)

# celery config
CELERY_BROKER_URL = "redis://localhost:6380/0"
CELERY_RESULT_BACKEND = "redis://localhost:6380/1"