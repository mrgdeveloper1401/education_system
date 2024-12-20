from education_system.base import *
from dj_database_url import config as dj_config
# from corsheaders.defaults import default_headers, default_methods

SECRET_KEY = config('PRODUCTION_SECRET_KEY', cast=str)

ALLOWED_HOSTS = ['*']

# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": config("PRODUCTION_DB_NAME", cast=str),
#         'USER': config("PRODUCTION_DB_USER", cast=str),
#         "PASSWORD": config("PRODUCTION_DB_PASSWORD", cast=str),
#         'HOST': config("PRODUCTION_DB_HOST", cast=str),
#         "PORT": config("PRODUCTION_DB_PORT", cast=int),
#     }
# }


DATABASES = {
    "default": dj_config(default=config('LIARA_POSTDB_URL', cast=str))
}

SIMPLE_JWT['SIGNING_KEY'] = SECRET_KEY

MIDDLEWARE += [
    "whitenoise.middleware.WhiteNoiseMiddleware",
]
MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware')

CORS_ORIGIN_ALLOW_ALL = True

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

STORAGES["staticfiles"] = {
    "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
}
