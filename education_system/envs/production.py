from education_system.base import *


SECRET_KEY = config('PRODUCTION_SECRET_KEY', cast=str)

ALLOWED_HOSTS = ''.join(config("PRODUCTION_ALLOWED_HOSTS", cast=list)).split(",")

MIDDLEWARE.insert(0, 'corsheaders.middleware.CorsMiddleware',)
MIDDLEWARE += [
    "whitenoise.middleware.WhiteNoiseMiddleware",
]


CORS_ALLOWED_ORIGINS = ''.join(config("CORS_ALLOW_ORIGINS_CORS", cast=list)).split(",")


# docker compose
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("POSTDB_NAME", cast=str),
        'USER': config("POSTDB_USER", cast=str),
        "PASSWORD": config("POSTDB_PASSWORD", cast=str),
        'HOST': config("POSTDB_HOST", cast=str),
        "PORT": config("POSTDB_PORT", cast=str, default="5432"),
    },
    "OPTIONS": {
        "pool": True
    }
}

SIMPLE_JWT['SIGNING_KEY'] = SECRET_KEY
# SIMPLE_JWT["AUDIENCE"] = config("AUDIENCE", cast=str)
# SIMPLE_JWT["ISSUER"] = config("ISSUER", cast=str)


SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
# CSRF_USE_SESSIONS = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"
SECURE_REFERRER_POLICY = "strict-origin"
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
CSRF_COOKIE_AGE = 3600
USE_X_FORWARDED_PORT = True
SESSION_COOKIE_DOMAIN = "api.codeima.ir"
CSRF_COOKIE_DOMAIN = "api.codeima.ir"

# STATIC_URL = config('STATIC_URL', cast=str)
# STATIC_ROOT = BASE_DIR / config("STATIC_ROOT", cast=str)
#
# MEDIA_URL = config("MEDIA_URL", cast=str)
# MEDIA_ROOT = config("MEDIA_ROOT", cast=str)


STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
    },
}
# print(STORAGES)

# celery compose config
CELERY_BROKER_URL = "redis://education_redis:6379/0"
CELERY_RESULT_BACKEND = "redis://education_redis:6379/1"

# jwt
SIMPLE_JWT["AUTH_COOKIE_DOMAIN"] = "codeima.ir" # A string like "example.com", or None for standard domain cookie.
SIMPLE_JWT['AUTH_COOKIE_SECURE'] = True # Whether the auth cookies should be secure (https:// only).

# cache config
CACHES['default']['LOCATION'] = "redis://education_redis:6379/3"