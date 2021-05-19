"""
Filename: plcserviceordersocket.py
Version name: 0.1, 2021-05-17
Short description: Module for tcp communication with PLC regarding servicerequests

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

import socket
from threading import Thread
import time

from .serviceorderhandler import ServiceOrderHandler
from .safteymonitoring import SafteyMonitoring
from mesapi.models import Setting


class PLCServiceOrderSocket(object):

    def __init__(self):
        self.serviceOrderHandler = ServiceOrderHandler()
        # socket params
        hostname = socket.gethostname()
        self.HOST = socket.gethostbyname(hostname)
        self.PORT = 2000
        self.ADDR = (self.HOST, self.PORT)
        self.BUFFSIZE = 512
        # setting up socket for server
        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER.bind(self.ADDR)
        # setting up forwarding if server should be in bridging mode
        settings = Setting.objects.all().first()
        self.isBridging = settings.isInBridgingMode
        self.ipAdressMES4 = settings.ipAdressMES4
        self.CLIENT = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if self.isBridging:
            self.CLIENT.connect((self.ipAdressMES4, self.PORT))

    # Thread for the cyclic communication. Receives messages from plc and gives them to SafteyMonitoring
    # @params:
    # client: socket of the plc
    # addr: ipv4 adress of the plc

    def serviceCommunication(self, client, addr):
        while True:
            msg = client.recv(self.BUFFSIZE)
            # if Socket is in bridging mode forward connection
            if self.isBridging:
                self.CLIENT.send(msg)
            # decode message
            if msg:
                # create and send response
                response = ""
                print(msg.decode("utf8"))
                response = self.serviceOrderHandler.createResponse(
                    msg=str(msg.decode("utf8")), ipAdress=addr)
                if response:
                    try:
                        client.send(response.encode("utf8"))
                    except Exception:
                        pass
            #!!! In finaler Implementierung wieder entfernen und durch timer ersetzen
            elif not msg:
                client.close()
                print("[CONNECTION]: Connection " + str(addr) + " closed")
                break

    # Waits for a connection from a plc. When a plc connects,
    # it starts a new thread for the cyclic communication

    def waitForConnection(self):
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

        self.SERVER.listen()
        print("[CONNECTION] PLCServiceOrderSocket-Server started")
        # Start Tcp server on seperate Thread
        SERVER_THREADING = Thread(target=self.waitForConnection)
        SERVER_THREADING.start()
        # Join all threads together
        SERVER_THREADING.join()
        # Close server if all connections crashed
        self.SERVER.close()
