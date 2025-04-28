from django.apps import AppConfig


class OrderAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'order_app'

    def ready(self):
        import order_app.signals
