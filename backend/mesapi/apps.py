from django.apps import AppConfig


class MesapiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mesapi"

    def ready(self):
        from .models import StatePLC

        # # undock all robotinos
        # plcs = StatePLC.objects.all()
        # for plc in plcs:
        #     if plc.id >6:
        #         plc.dockedAt = 0
        #         plc.save()

        return super().ready()
