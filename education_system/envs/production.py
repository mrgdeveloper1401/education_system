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

# use database liara with connect by defaul
# DATABASES = {
#     'default': {
#         "ENGINE": "django.contrib.gis.db.backends.postgis",
#         "HOST": config("LIARA_DB_HOST", cast=str),
#         "PASSWORD": config("LIARA_DB_PASSWORD", cast=str),
#         "USER": config("LIARA_DB_USER", cast=str),
#         "PORT": config("LIARA_DB_PORT", cast=int),
#         "NAME": config("LIARA_DB_NAME", cast=str)
#     }
# }

SIMPLE_JWT['SIGNING_KEY'] = SECRET_KEY

MIDDLEWARE += [
   'corsheaders.middleware.CorsMiddleware',
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = '*'
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = [
 "DELETE",
 "GET",
 "OPTIONS",
 "PATCH",
 "POST",
 "PUT",
]


MIDDLEWARE += [
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

STORAGES = {
    # ...
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
    }
}

AWS_ACCESS_KEY_ID = config('ARVAN_AWS_ACCESS_KEY_ID', cast=str)
AWS_SECRET_ACCESS_KEY = config('ARVAN_AWS_SECRET_ACCESS_KEY', cast=str)
AWS_STORAGE_BUCKET_NAME = config('ARVAN_AWS_STORAGE_BUCKET_NAME', cast=str)
AWS_S3_ENDPOINT_URL = config('ARVAN_AWS_S3_ENDPOINT_URL', cast=str)
AWS_S3_REGION_NAME = 'us-east-1'
AWS_S3_FILE_OVERWRITE = False
AWS_SERVICE_NAME = 's3'

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "SAMEORIGIN"
SECURE_REFERRER_POLICY = "strict-origin"
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS += [
    "storages",
]
