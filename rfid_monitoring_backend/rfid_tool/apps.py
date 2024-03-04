from django.apps import AppConfig


class RfidToolConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "rfid_tool"

    def ready(self):
        import rfid_tool.signals  # noqa
