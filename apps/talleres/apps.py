from django.apps import AppConfig


class TalleresConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.talleres'
    verbose_name = 'Talleres'

    def ready(self):
        import apps.talleres.signals  # noqa: F401
