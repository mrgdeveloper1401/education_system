import os
from datetime import timedelta
from pathlib import Path
from decouple import config, Csv
from django.utils import timezone
from kombu import Queue

from base.dj_ckeditor_config import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", default=True, cast=bool)

# allowed host
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv(), default="*")

# secret key
SECRET_KEY = config(
    "SECRET_KEY",
    cast=str,
    default="secret_olfati_2f026_salam_donna_why_ali_reza_hossein",
)

# secret key fall back
USE_FALL_BACK_SECRET_KEY = config("USE_FALL_BACK_SECRET_KEY", cast=bool, default=False)
if USE_FALL_BACK_SECRET_KEY:
    DJANGO_SECRET_KEY_FALLBACKS = config("DJANGO_SECRET_KEY_FALLBACKS", cast=str)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Application definition
THIRD_PARTY_PACKAGE = [
    "drf_spectacular",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "treebeard",
    "import_export",
    "django_ckeditor_5",
    "django_celery_beat",
    "drf_spectacular_sidecar",
    "adrf",
]

THIRD_PARTY_APP = [
    'apps.account_app',
    'apps.core_app',
    "apps.advertise_app",
    "apps.course_app",
    "apps.subscription_app",
    "apps.blog_app",
    "apps.exam_app",
    "apps.discount_app",
    "apps.order_app"
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    *THIRD_PARTY_PACKAGE,
    *THIRD_PARTY_APP,
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "base.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

USE_ASGI = config("USE_ASGI", default=True, cast=bool)
if USE_ASGI:
    ASGI_APPLICATION = "base.asgi.application"
else:
    WSGI_APPLICATION = "base.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": config(
            "PGDB_ENGINE", default="django.db.backends.postgresql", cast=str
        ),
        "NAME": config("POSTDB_NAME", cast=str, default="education"),
        "USER": config("POSTDB_USER", cast=str, default="postgres"),
        "PASSWORD": config("POSTDB_PASSWORD", cast=str, default="postgres"),
        "HOST": config("POSTDB_HOST", cast=str, default="127.0.0.1"),
        "PORT": config("POSTDB_PORT", cast=int, default=5433),
        "OPTIONS": {
            "pool": True
        },
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    }
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/
LANGUAGE_CODE = "en-us"

TIME_ZONE = config("TIME_ZONE", cast=str, default="Asia/Tehran")

USE_I18N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = 'account_app.User'

REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': ('django_filters.rest_framework.DjangoFilterBackend',)

}

SPECTACULAR_SETTINGS = {
    'TITLE': 'education system',
    'DESCRIPTION': 'Your project description',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    # 'IGNORE_WARNINGS': ['drf_spectacular.W001'],
    'SWAGGER_UI_DIST': 'SIDECAR',  # shorthand to use the sidecar instead
    'SWAGGER_UI_FAVICON_HREF': 'SIDECAR',
    'REDOC_DIST': 'SIDECAR',
}

ACCESS_TOKEN_LIFETIME = config("ACCESS_TOKEN_LIFETIME", cast=int, default=7)
REFRESH_TOKEN_LIFETIME = config("REFRESH_TOKEN_LIFETIME", cast=int, default=365)
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=ACCESS_TOKEN_LIFETIME),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=REFRESH_TOKEN_LIFETIME),
}

# default storages
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}

# config django storage
USE_DJANGO_STORAGES = config("USE_DJANGO_STORAGES", cast=bool, default=True)
if USE_DJANGO_STORAGES:
    STORAGES["default"]["BACKEND"] = "storages.backends.s3.S3Storage"
    AWS_S3_REGION_NAME = "eu-west-1"
    AWS_DEFAULT_ACL = "public-read"
    AWS_QUERYSTRING_AUTH = config("AWS_QUERYSTRING_AUTH", default=False, cast=bool)
    AWS_ACCESS_KEY_ID = config("S3_ACCESS_KEY", cast=str, default="")
    AWS_SECRET_ACCESS_KEY = config("S3_SECRET_KEY", cast=str, default="")
    AWS_STORAGE_BUCKET_NAME = config("S3_BUCKET_NAME", cast=str, default="")
    AWS_S3_ENDPOINT_URL = config("S3_ENDPOINT_URL", cast=str, default="")
    AWS_S3_FILE_OVERWRITE = config("S3_FILE_OVERWRITE", cast=bool, default=False)
    AWS_S3_MAX_MEMORY_SIZE = config(
        "S3_MAX_MEMORY_SIZE", cast=int, default=2097152
    )  # byte --> 2MB
else:
    MEDIA_ROOT = BASE_DIR / "media"  # upload file into dir
    MEDIA_URL = "/media/"  # address in url

# CKEDITOR_5_CUSTOM_CSS = 'path_to.css'
CKEDITOR_5_ALLOW_ALL_FILE_TYPES = True

# ckeditor path
CKEDITOR_BASEPATH = BASE_DIR / "staticfiles/ckeditor/ckeditor/"

# Celery settings
# celery config
USE_CELERY = config("USE_CELERY", cast=bool, default=True)
if USE_CELERY:
    CELERY_BROKER_URL = config(
        "CELERY_BROKER_URL", cast=str, default="redis://localhost:6381/5"
    )
    CELERY_RESULT_BACKEND = config(
        "CELERY_RESULT_BACKEND", cast=str, default="redis://localhost:6381/6"
    )  # نتیجه تسک در کجا ریخته شود
    CELERY_TIMEZONE = config(
        "CELERY_TIMEZONE", cast=str, default=TIME_ZONE
    )  # منطقه زمانی Celery برای زمان‌بندی تسک‌ها
    CELERY_ACCEPT_CONTENT = config(
        "CELERY_ACCEPT_CONTENT", cast=Csv(), default="json"
    )  # فرمت‌های مجاز برای دریافت پیام‌های تسک
    CELERY_TASK_SERIALIZER = config(
        "CELERY_TASK_SERIALIZER", cast=str, default="json"
    )  # فرمت serialize کردن خودِ تسک هنگام ارسال به صف
    CELERY_RESULT_SERIALIZER = config(
        "CELERY_RESULT_SERIALIZER", cast=str, default="json"
    )  # فرمت serialize کردن نتیجه‌ی تسک
    CELERY_TASK_ACKS_LATE = config(
        "CELERY_TASK_ACKS_LATE", cast=bool, default=True
    )  # تسک در صورت عدم انجام دوباره انجام میشود
    CELERY_WORKER_PREFETCH_MULTIPLIER = config(
        "WORKER_PREFETCH_MULTIPLIER", cast=int, default=1
    )  # هر Worker قبل از اتمام تسک فعلی چند تسک از صف بردارد
    CELERY_TASK_ALWAYS_EAGER = config(
        "CELERY_TASK_ALWAYS_EAGER", cast=bool, default=False
    )  # اگر True باشد، تسک‌ها واقعاً async اجرا نمی‌شوند و همان لحظه محلی اجرا می‌شوند
    CELERY_TASK_TIME_LIMIT = config(
        "CELERY_TASK_TIME_LIMIT", cast=int, default=30
    )  # حداکثر زمان مجاز اجرای هر تسک (ثانیه)
    CELERY_ENABLE_UTC = config(
        "CELERY_ENABLE_UTC", cast=bool, default=True
    )  # اگر True باشد، Celery زمان‌ها را بر اساس UTC مدیریت می‌کند
    CELERY_WORKER_CONCURRENCY = config(
        "WORKER_CONCURRENCY", cast=int, default=8
    )  # تعداد پردازش/ورکر همزمان برای اجرای تسک‌ها
    CELERY_WORKER_MAX_TASKS_PER_CHILD = config(
        "WORKER_MAX_TASKS_PER_CHILD", cast=int, default=1000
    )  # بعد از چند تسک، Worker child ری‌استارت شود تا از memory leak جلوگیری شود
    CELERY_WORKER_MAX_MEMORY_PER_CHILD = config(
        "WORKER_MAX_MEMORY_PER_CHILD", cast=int, default=200000
    )  # اگر مصرف حافظه Worker child از این مقدار (کیلوبایت) بیشتر شد، ری‌استارت شود

# define queue
CELERY_TASK_QUEUES = (
    Queue("otp"),
    Queue("coupon_send"),
    Queue("advertise"),
    Queue("reminder"),
    Queue("course_signup"),
    Queue("referral_process"),
    Queue("create_qrcode"),
    Queue("notification")
)

# celery beat config
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# cache config
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": config(
            "PROD_REDIS_LOCATION", cast=str, default="redis://localhost:6381/1"
        ),
        "OPTIONS": {
            "SERIALIZER": config(
                "REDIS_DEFAULT_SERIALIZER",
                cast=str,
                default="django_redis.serializers.msgpack.MSGPackSerializer",
            ),
            "SOCKET_CONNECT_TIMEOUT": config(
                "SOCKET_DEFAULT_CONNECT_TIMEOUT", default=5, cast=int
            ),
            "SOCKET_TIMEOUT": config("SOCKET_DEFAULT_TIMEOUT", default=5, cast=int),
            "TIMEOUT": config("CACHE_DEFAULT_TIMEOUT", cast=int, default=1209600),
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "CONNECTION_POOL_KWARGS": {
                "max_connections": config("REDIS_MAX_CONNECTION", cast=int, default=20),
                "retry_on_timeout": config(
                    "REDIS_DEFAULT_POOL_RETRY_TIMEOUT", default=True, cast=bool
                ),
                "health_check_interval": config(
                    "REDIS_DEFAULT_HEALTH_CHECK_INTERVAL", default=True, cast=bool
                ),
                "socket_keepalive": config(
                    "REDIS_DEFAULT_SOCKET_KEEPALIVE", default=True, cast=bool
                ),
            },
        },
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

ZIBAL_CALLBACK_URL = config("ZIBAL_CALLBACK_URL", cast=str)
ZIBAL_MERCHENT_ID = config("ZIBAL_MERCHENT_ID", cast=str)

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db' # cache session database

# debug toolbar
USE_DEBUG_TOOLBAR = config("USE_DEBUG_TOOLBAR", default=True, cast=bool)
if USE_DEBUG_TOOLBAR:
    INSTALLED_APPS.append(
        "debug_toolbar",
    )
    MIDDLEWARE.append(
        "debug_toolbar.middleware.DebugToolbarMiddleware",
    )
    INTERNAL_IPS = [
        "127.0.0.1",
    ]

# django-extensions
USE_DJ_EXTENSIONS = config("USE_DJ_EXTENSIONS", default=True, cast=bool)
if USE_DJ_EXTENSIONS:
    INSTALLED_APPS.append("django_extensions")

USE_SSL_CONFIG = config("USE_SSL_CONFIG", cast=bool, default=False)
if USE_SSL_CONFIG:
    # Https/ssl settings
    # SECURE_SSL_REDIRECT = True  # redirect http request into https request
    SECURE_SSL_REDIRECT = False  # ریدایرکت در سطح Nginx انجام می‌شود
    USE_X_FORWARDED_HOST = True  # use header x-forwarded-host
    USE_X_FORWARDED_PORT = True  # use header x-forwarded-port

    # HSTS settings
    SECURE_HSTS_SECONDS = 31536000  # 1 year, hsts validity period
    SECURE_HSTS_PRELOAD = True  #
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True  # active hsts into subdomain

    # cookie
    SESSION_COOKIE_SECURE = True  # session cookie only https
    SESSION_COOKIE_DOMAIN = config(
        "SESSION_COOKIE_DOMAIN", cast=str
    )  # for example --> .example.com, domain cookie
    SESSION_COOKIE_HTTPONLY = True  # prevent access with by javascript

    # csrf
    CSRF_COOKIE_SECURE = True  # send cookie csrf only https
    CSRF_COOKIE_HTTPONLY = True  # csrf prevent access javascript
    CSRF_COOKIE_SAMESITE = "Strict"  # Prevent cookie requests on cross-site requests
    CSRF_COOKIE_DOMAIN = config(
        "CSRF_COOKIE_DOMAIN", cast=str
    )  # for example --> .example.com, domain csrf cookie
    CSRF_COOKIE_AGE = 3600  # csrf cookie validity period

    # Content Security Settings
    SECURE_CONTENT_TYPE_NOSNIFF = True  # prevent mime sniffing
    SECURE_BROWSER_XSS_FILTER = True  # active filter xss in browser
    SECURE_REFERRER_POLICY = (
        "strict-origin-when-cross-origin"  # control information  on source request
    )
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

    # Frame & Clickjacking Protection
    X_FRAME_OPTIONS = "DENY"  # prevent show iframe


# use cors
USE_CORS = config("USE_CORS", default=False, cast=bool)
if USE_CORS:
    MIDDLEWARE.insert(0, "corsheaders.middleware.CorsMiddleware")
    CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", cast=Csv())
    INSTALLED_APPS.append("corsheaders")

    USE_DEV_CORS = config("USE_DEV_CORS", default=False, cast=bool)
    if USE_DEV_CORS:
        CORS_ALLOWED_ORIGINS.append("http://localhost:3000")

# config log
USE_LOG = config("USE_LOG", cast=bool, default=True)
if USE_LOG:  # TODO, cron job for clean log every 2 days and show log in panel admin for superuser
    log_dir = os.path.join("general_log_django", timezone.now().strftime("%Y-%m-%d"))
    os.makedirs(log_dir, exist_ok=True)
    LOGGING = {
        "version": 1,
        "disable_existing_loggers": False,
        "handlers": {
            "error_file": {
                "level": "ERROR",
                "class": "logging.FileHandler",
                "filename": os.path.join(log_dir, "error_file.log"),
            },
            "warning_file": {
                    "level": "WARNING",
                "class": "logging.FileHandler",
                "filename": os.path.join(log_dir, "warning_file.log"),
            },
            "critical_file": {
                "level": "CRITICAL",
                "class": "logging.FileHandler",
                "filename": os.path.join(log_dir, "critical_file.log"),
            },
        },
        "loggers": {
            "django": {
                "handlers": ["critical_file", "error_file", 'warning_file'],
                "propagate": True,
            }
        },
    }
if DEBUG and USE_LOG:
    LOGGING["handlers"]["console"] = {
        "class": "logging.StreamHandler",
        "level": "INFO",
    }
    LOGGING["loggers"]["django"]["handlers"].append("console")