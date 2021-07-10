"""
Filename: plcstatesocket.py
Version name: 1.0, 2021-07-10
Short description: Module for cyclic tcp communications with the plc

(C) 2003-2021 IAS, Universitaet Stuttgart

"""
import django
import socket
import binascii
from threading import Thread
import time


class PLCStateSocket(object):

    def __init__(self):
        # socket params
        from django.apps import apps
        from .systemmonitoring import SystemMonitoring
        self.systemMonitoring = SystemMonitoring()
        self.HOST = "129.69.102.129"
        self.PORT = 2001
        self.ADDR = (self.HOST, self.PORT)
        self.BUFFSIZE = 512
        # setting up socket for server
        self.SERVER = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.SERVER.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.SERVER.bind(self.ADDR)

    # Thread for the cyclic communication. Receives messages from plc and gives them to SafteyMonitoring
    # @params:
    #   client: socket of the plc
    #   addr: ipv4 adress of the plc
    def cyclicCommunication(self, client, addr):
        startTime = time.time()
        while True:
            msg = client.recv(self.BUFFSIZE)
            # decode message
            if msg:
                startTime = time.time()
                msg = binascii.hexlify(msg).decode()
                self.systemMonitoring.decodeCyclicMessage(
                    msg=str(msg), ipAdress=addr)
            elif not msg:
                # Close connection if there was no message in last 10 seconds
                if time.time() - startTime > 5:
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
        django.setup()
        # delete all robotinos
        self.SERVER.listen()
        print("[CONNECTION] PLCStateSocket-Server started")
        # Start Tcp server on seperate Thread
        SERVER_THREADING = Thread(target=self.waitForConnection)
        try:
            SERVER_THREADING.start()
            SERVER_THREADING.join()
        except Exception as e:
            print(e)
        # Close server if all connections crashed
        self.SERVER.close()
