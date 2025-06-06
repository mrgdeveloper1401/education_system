from django.apps import AppConfig


class AdvertiseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "advertise"

    def ready(self):
        import advertise.signals
