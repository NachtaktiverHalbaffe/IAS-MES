import socket
from django.test import TestCase
# Create your tests here.


# Test PLCStateSocket
class TestPLCStateSocket(object):

    def __init__(self):
        self.PORT = 2001
        self.FORMAT = 'utf-8'
        self.SERVER = "192.168.178.30"
        self.ADDR = (self.SERVER, self.PORT)

    def sendTestMessage(self, msg):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(self.ADDR)
        client.send(msg.encode(self.FORMAT))
        client.close()


print("Starting Test of cyclic state communication with the PLC")
test = TestPLCStateSocket()
test.sendTestMessage('0x000x020x020x82')
print("Test messgage send. Now sending invalid data")
test.sendTestMessage('0x000x020x040x82')
print("Invalid data send.")
