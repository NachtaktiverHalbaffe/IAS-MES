from django.apps import AppConfig
from multiprocessing import Process


class MesapiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "mesapi"

    def ready(self):
        from mesbackend.plcserviceordersocket import PLCServiceOrderSocket
        from mesbackend.plcstatesocket import PLCStateSocket

        serviceProcess = Process(target=PLCServiceOrderSocket().runServer)
        stateProcess = Process(target=PLCStateSocket().runServer)
        # serviceProcess.daemon = True
        # stateProcess.daemon = True
        serviceProcess.start()
        stateProcess.start()
        return super().ready()
