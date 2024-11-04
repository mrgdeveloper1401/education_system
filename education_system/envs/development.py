# from education_system.base import *
#
# SECRET_KEY = config('DEVELOP_SECRET_KEY', cast=str)
#
#
# DATABASES = {
#     "default": {
#         "ENGINE": "django.db.backends.postgresql",
#         "NAME": 'education_system',
#         'USER': "postgres",
#         "PASSWORD": "postgres",
#         'HOST': "localhost",
#         "PORT": 5432,
#     }
# }
#
# INSTALLED_APPS += [
#     "debug_toolbar",
# ]
#
# MIDDLEWARE += [
#     "debug_toolbar.middleware.DebugToolbarMiddleware",
# ]
#
# INTERNAL_IPS = [
#     # ...
#     "127.0.0.1",
#     # ...
# ]
#
# SIMPLE_JWT['SIGNING_KEY'] = SECRET_KEY
