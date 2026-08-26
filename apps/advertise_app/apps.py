from django.apps import AppConfig


class AdvertiseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.advertise_app"

    def ready(self):
        import apps.advertise_app.signals
