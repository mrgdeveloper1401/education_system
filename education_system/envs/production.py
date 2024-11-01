from education_system.settings import *

SECRET_KEY = config('PRODUCTION_SECRET_KEY', cast=str)

ALLOWED_HOSTS = ['*']

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": 'postgres',
#         'USER': "root",
#         "PASSWORD": "UwIyKoT9U94eYKrtVpmT4lfu",
#         'HOST': "education-systemdb",
#         "PORT": 5432,
#     }
# }

DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.postgresql",
        "HOST": "education_system",
        "PASSWORD": "postgres",
        "USER": "postgres",
        "PORT": "5432",
        "NAME": "postgres"
    }
}
