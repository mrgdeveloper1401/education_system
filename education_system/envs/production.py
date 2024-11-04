from education_system.base import *
from dj_database_url import config as dj_config

SECRET_KEY = config('PRODUCTION_SECRET_KEY', cast=str)

ALLOWED_HOSTS = ['*']

# use system
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

# user docker compose
# DATABASES = {
#     'default': {
#         "ENGINE": "django.db.backends.postgresql",
#         "HOST": "education_system",
#         "PASSWORD": "postgres",
#         "USER": "postgres",
#         "PORT": "5432",
#         "NAME": "postgres"
#     }
# }

# use database liara with connect by url
DATABASES = {
    'default': dj_config(default=config("DATABASE_URL", cast=str)),
}

SIMPLE_JWT['SIGNING_KEY'] = SECRET_KEY
