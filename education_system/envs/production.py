from education_system.base import *


SECRET_KEY = config('PRODUCTION_SECRET_KEY', cast=str)

ALLOWED_HOSTS = ''.join(config("PRODUCTION_ALLOWED_HOSTS", cast=list)).split(",")

MIDDLEWARE += [
    "whitenoise.middleware.WhiteNoiseMiddleware",
]

CORS_ALLOWED_ORIGINS = ''.join(config("CORS_ALLOW_ORIGINS_CORS", cast=list)).split(",")
print(CORS_ALLOWED_ORIGINS)

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
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("VPS_PRODUCTION_DB_NAME", cast=str),
        'USER': config("VPS_PRODUCTION_DB_USER", cast=str),
        "PASSWORD": config("VPS_PRODUCTION_DB_PASSWORD", cast=str),
        'HOST': config("VPS_PRODUCTION_DB_HOST", cast=str),
        "PORT": config("VPS_PRODUCTION_DB_PORT", cast=int),
    }
}

SIMPLE_JWT['SIGNING_KEY'] = SECRET_KEY
# SIMPLE_JWT["AUDIENCE"] = config("AUDIENCE", cast=str)
# SIMPLE_JWT["ISSUER"] = config("ISSUER", cast=str)


SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'
CSRF_USE_SESSIONS = True
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

# STATIC_URL = config('STATIC_URL', cast=str)
# STATIC_ROOT = BASE_DIR / config("STATIC_ROOT", cast=str)
#
# MEDIA_URL = config("MEDIA_URL", cast=str)
# MEDIA_ROOT = config("MEDIA_ROOT", cast=str)


STORAGES["staticfiles"] = {
    "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
}
