from django.apps import AppConfig


class BlogAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.blog_app"

    def ready(self):
        import apps.blog_app.signals
