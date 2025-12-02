import datetime
import os.path
from datetime import timedelta
from pathlib import Path
from decouple import config, Csv
from kombu import Queue

from education_system.dj_ckeditor_config import CKEDITOR_5_CONFIGS, customColorPalette

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Application definition

DEBUG = config("DEBUG", cast=bool, default=False)

THIRD_PARTY_PACKAGE = [
    "drf_spectacular",
    "rest_framework",
    "rest_framework_simplejwt",
    # "storages",
    "django_filters",
    "treebeard",
    "import_export",
    "django_ckeditor_5",
    "django_celery_beat",
    "drf_spectacular_sidecar",
    "adrf",
]

THIRD_PARTY_APP = [
    'accounts.apps.AccountsConfig',
    'core.apps.CoreConfig',
    'images.apps.ImagesConfig',
    "advertise.apps.AdvertiseConfig",
    "course.apps.CourseConfig",
    "subscription_app.apps.SubscriptionAppConfig",
    "main_settings.apps.MainSettingsConfig",
    "blog_app.apps.BlogAppConfig",
    "chat_app.apps.ChatAppConfig",
    "exam_app.apps.ExamAppConfig",
    "discount_app.apps.DiscountAppConfig",
    "order_app.apps.OrderAppConfig"
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

ROOT_URLCONF = "education_system.urls"

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

# WSGI_APPLICATION = "education_system.wsgi.application"
ASGI_APPLICATION = "education_system.asgi.application"


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

TIME_ZONE = "Asia/Tehran"

USE_I18N = True

USE_TZ = True


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = 'accounts.User'

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

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=30),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': False,
    "AUTH_HEADER_TYPES": ("Bearer",),
    'ALGORITHM': 'HS256',
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,

    'AUTH_HEADER_NAME': 'HTTP_AUTHORIZATION',
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'rest_framework_simplejwt.authentication.default_user_authentication_rule',

    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',

    'JTI_CLAIM': 'jti',

    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),

    # custom
    'AUTH_COOKIE': 'access_token',  # Cookie name. Enables cookies if value is set.
    'AUTH_COOKIE_HTTP_ONLY': True,  # Http only cookie flag.It's not fetch by javascript.
    'AUTH_COOKIE_PATH': '/',  # The path of the auth cookie.
    'AUTH_COOKIE_SAMESITE': 'Lax',
}

# with logging django
log_dir = os.path.join(BASE_DIR / 'general_log_django', datetime.date.today().strftime("%Y-%m-%d"))
os.makedirs(log_dir, exist_ok=True)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "color": {
            "()": "colorlog.ColoredFormatter",
            "format": "%(log_color)s%(levelname)s %(reset)s%(asctime)s %(module)s %(process)d %(thread)d %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    },
    "handlers": {
        "error_file": {
            "level": "ERROR",
            "class": "logging.FileHandler",
            "formatter": "color",
            "filename": os.path.join(BASE_DIR / log_dir / 'error_file.log')
        },
        "warning_file": {
            "level": "WARN",
            "class": "logging.FileHandler",
            "formatter": "color",
            "filename": os.path.join(BASE_DIR / log_dir / 'warning_file.log')
        },
        "critical_file": {
            "level": "CRITICAL",
            "class": "logging.FileHandler",
            "formatter": "color",
            "filename": os.path.join(BASE_DIR / log_dir / 'critical_file.log')
        },
    },
    "loggers": {
        "django": {
            "handlers": ["warning_file", "critical_file", "error_file"],
            'propagate': True,
        }
    }
}

# config django storage
AWS_ACCESS_KEY_ID = config('ARVAN_AWS_ACCESS_KEY_ID', cast=str)
AWS_SECRET_ACCESS_KEY = config('ARVAN_AWS_SECRET_ACCESS_KEY', cast=str)
AWS_STORAGE_BUCKET_NAME = config('ARVAN_AWS_STORAGE_BUCKET_NAME', cast=str)
AWS_S3_ENDPOINT_URL = config('ARVAN_AWS_S3_ENDPOINT_URL', cast=str)
AWS_S3_REGION_NAME = 'us-east-1'
AWS_DEFAULT_ACL = 'public-read'
AWS_QUERYSTRING_AUTH = False

# CKEDITOR_5_CUSTOM_CSS = 'path_to.css'
CKEDITOR_5_ALLOW_ALL_FILE_TYPES = True

# ckeditor path
CKEDITOR_BASEPATH = BASE_DIR / "staticfiles/ckeditor/ckeditor/"

# Celery settings
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Tehran'
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_WORKER_PREFETCH_MULTIPLIER = 1  # do the same time task in worker
CELERY_WORKER_CONCURRENCY = config("CELERY_WORKER_CONCURRENCY", cast=int, default=os.cpu_count())
CELERY_TASK_ACKS_LATE = True  # if not start, retry again

# define queue
CELERY_QUEUES = (
    # Queue("sms_otp"),
    Queue("coupon_send"),
    Queue("advertise"),
    Queue("reminder"),
    Queue("course_signup"),
    Queue("referral_process"),
    Queue("create_qrcode"),
    Queue("notification")
)

# define task route
CELERY_TASK_ROUTES = {
    # "accounts.tasks.send_sms_otp_code": {"queue": "sms_otp"},
    "accounts.tasks.send_sms_forget_password": {"queue": "sms_otp"},
    "advertise.tasks.send_sms_accept_advertise": {"queue": "advertise"},
    "order_app.tasks.send_successfully_signup": {"queue": "course_signup"},
    "order_app.tasks.process_referral": {"queue": "referral_process"},
    "order_app.tasks.coupon_send": {"queue": "coupon_send"},
    "course.tasks.create_qr_code": {"queue": "create_qrcode"},
    "course.tasks.admin_user_request_certificate": {"queue": "notification"},
    "course.tasks.send_notification_when_score_is_accepted": {"queue": "notification"},
    "subscription_app.tasks.send_sms_before_expire_subscription": {"queue": "reminder"},
}

# celery beat config
CELERY_BEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"

# cache config
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

BITPAY_MERCHANT_ID=config("GATEWAY_ID", cast=str)
BITPAY_CALLBACK_URL='https://api.codeima.ir/api_subscription/verify_payment/?trans_id={trans_id}&id_get={id_get}'

ZIBAL_CALLBACK_URL="https://codeima.ir//p-student/subscription/result-payment/"
ZIBAL_MERCHENT_ID=config("f", cast=str)

SESSION_ENGINE = 'django.contrib.sessions.backends.cached_db' # cache session database