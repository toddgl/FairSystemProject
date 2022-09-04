from django.apps import AppConfig


class FairsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fairs'

    def ready(self):
        import fairs.signals
