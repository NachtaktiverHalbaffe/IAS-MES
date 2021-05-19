"""
Filename: plcstatesocket.py
Version name: 0.1, 2021-05-17
Short description: Module for cyclic tcp communications with the plc

(C) 2003-2021 IAS, Universitaet Stuttgart

"""
import django
import socket
from threading import Thread
import time


class PLCStateSocket(object):

    def __init__(self):
        # socket params
        from django.apps import apps
        hostname = socket.gethostname()
        self.HOST = socket.gethostbyname(hostname)
        self.PORT = 2001
        self.ADDR = (self.HOST, self.PORT)
        self.BUFFSIZE = 512
        # setting up socket for server
        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.SERVER.bind(self.ADDR)
        # setting up forwarding if server should be in bridging mode
        settings = apps.get_model('mesapi', 'Setting')
        settings = settings.objects.all().first()
        self.isBridging = settings.isInBridgingMode
        self.ipAdressMES4 = settings.ipAdressMES4
        self.CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.isBridging:
            self.CLIENT.connect((self.ipAdressMES4, self.PORT))

    # Thread for the cyclic communication. Receives messages from plc and gives them to SafteyMonitoring
    # @params:
    # client: socket of the plc
    # addr: ipv4 adress of the plc

    def cyclicCommunication(self, client, addr):

        print(self.ipAdressMES4)
        while True:
            msg = client.recv(self.BUFFSIZE)
            # if Socket is in bridging mode forward connection
            if self.isBridging:
                self.CLIENT.send(msg)
            # decode message
            if msg:
                django.setup()
                from .systemmonitoring import SystemMonitoring
                SystemMonitoring().decodeCyclicMessage(
                    msg=str(msg.decode("utf8")), ipAdress=addr)
            #!!! In finaler Implementierung wieder entfernen und durch timer ersetzen
            elif not msg:
                client.close()
                print("[CONNECTION]: Connection " + str(addr) + " closed")
                break

    # Waits for a connection from a plc. When a plc connects,
    # it starts a new thread for the cyclic communication

    def waitForConnection(self):
        from .safteymonitoring import SafteyMonitoring
        while True:
            try:
                client, addr = self.SERVER.accept()
                print("[CONNECTION]: " + str(addr) + "connected to socket")
                Thread(target=self.cyclicCommunication,
                       args=(client, addr)).start()
            except Exception as e:
                SafteyMonitoring().decodeError(
                    errorLevel=SafteyMonitoring().LEVEL_ERROR, errorCategory=SafteyMonitoring().CATEGORY_CONNECTION, msg=e)
                break

    # Starts and runs the tcpserver. When the server crashes in waitForConnection(), it will close the server

    def runServer(self):

        self.SERVER.listen()
        print("[CONNECTION] PLCStateSocket-Server started")
        # Start Tcp server on seperate Thread
        SERVER_THREADING = Thread(target=self.waitForConnection)
        SERVER_THREADING.start()
        # Join all threads together
        SERVER_THREADING.join()
        # Close server if all connections crashed
        self.SERVER.close()
