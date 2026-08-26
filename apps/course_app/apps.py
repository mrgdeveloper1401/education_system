from django.apps import AppConfig


class CourseConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.course_app"

    def ready(self):
        import apps.course_app.signals
