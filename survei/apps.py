from django.apps import AppConfig

class SurveiConfig(AppConfig):
    name = "survei"              # this must match your app folder name
    default_auto_field = "django.db.models.BigAutoField"

    def ready(self):
        # this import must be here—no typos!
        import survei.signals     # noqa
