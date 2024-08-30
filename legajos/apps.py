from django.apps import AppConfig


class LegajoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "Legajos"

    def ready(self):
        import legajos.signals  # pylint: disable=unused-import, import-outside-toplevel
