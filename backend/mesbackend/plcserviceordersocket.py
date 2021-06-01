"""
Filename: plcserviceordersocket.py
Version name: 0.1, 2021-05-19
Short description: Module for tcp communication with PLC regarding servicerequests

(C) 2003-2021 IAS, Universitaet Stuttgart

"""


import socket
from threading import Thread
import time
import django


class PLCServiceOrderSocket(object):

    def __init__(self):
        from django.apps import apps
        # socket params
        hostname = socket.gethostname()
        self.HOST = socket.gethostbyname(hostname)
        self.PORT = 2000
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

    # Thread for the service communication.
    # @params:
    # client: socket of the plc
    # addr: ipv4 adress of the plc

    def serviceCommunication(self, client, addr):
        #django.setup()
        startTime = time.time()
        while True:
            msg = client.recv(self.BUFFSIZE)
            # if Socket is in bridging mode forward connection
            if self.isBridging:
                self.CLIENT.send(msg)
            # decode message
            if msg:
                # make sure apps and models are loaded
                from .serviceorderhandler import ServiceOrderHandler
                # create and send response
                startTime = time.time()
                response = ServiceOrderHandler().createResponse(
                    msg=str(msg.decode("utf8")), ipAdress=addr)
                if response:
                    try:
                        client.send(response.encode("utf8"))
                    except Exception:
                        pass
            elif not msg:
                # Close connection if there was no message in last 10 seconds
                if time.time() - startTime > 10:
                    client.close()
                    print("[CONNECTION]: Connection " + str(addr) + " closed")
                    break

                # Waits for a connection from a plc. When a plc connects,
                # it starts a new thread for the service specific communication

    def waitForConnection(self):
        from .safteymonitoring import SafteyMonitoring
        safteyMonitoring = SafteyMonitoring()
        while True:
            try:
                client, addr = self.SERVER.accept()
                print("[CONNECTION]: " + str(addr) + "connected to socket")
                Thread(target=self.serviceCommunication,
                       args=(client, addr)).start()
            except Exception as e:
                safteyMonitoring.decodeError(
                    errorLevel=safteyMonitoring.LEVEL_ERROR, errorCategory=safteyMonitoring.CATEGORY_CONNECTION, msg=e)
                break

    # Starts and runs the tcpserver. When the server crashes in waitForConnection(), it will close the server

    def runServer(self):
        django.setup()
        self.SERVER.listen()
        print("[CONNECTION] PLCServiceOrderSocket-Server started")
        # Start Tcp server on seperate Thread
        SERVER_THREADING = Thread(target=self.waitForConnection)
        try:
            SERVER_THREADING.start()
            SERVER_THREADING.join()
        except Exception as e:
            pass
        # Close server if all connections crashed
        self.SERVER.close()
