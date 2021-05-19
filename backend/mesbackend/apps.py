from django.apps import AppConfig


class MesbackendConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mesbackend'

    def ready(self):
        import mesbackend.signals
        return super().ready()
