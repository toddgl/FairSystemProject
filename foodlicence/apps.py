from django.apps import AppConfig


class FoodlicenseConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'foodlicence'

    def ready(self):
        import foodlicence.signals
