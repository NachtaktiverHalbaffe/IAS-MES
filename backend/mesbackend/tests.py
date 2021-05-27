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


class TestPLCServiceOrderSocket(object):

    def __init__(self):
        self.PORT = 2000
        self.FORMAT = 'utf-8'
        self.SERVER = "192.168.178.30"
        self.ADDR = (self.SERVER, self.PORT)

    def sendTestMessage(self, msg):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(self.ADDR)
        client.send(msg.encode(self.FORMAT))
        print("message send")
        while True:
            response = client.recv(2048).decode(self.FORMAT)
            if response:
                print(response)
                break
        client.close()


print("Starting Test of cyclic state communication with the PLC")
test = TestPLCStateSocket()
try:
    test.sendTestMessage('00010285')
    print("Test messgage send. Now sending invalid data")
    # test.sendTestMessage('0x000x020x040x82')
    # print("Invalid data send.")
except Exception as e:
    print("Test failed")
    print(e)

print("Starting Test of service order communication with the PLC")
test2 = TestPLCServiceOrderSocket()
try:
    test2.sendTestMessage("3333330200020064000400000000000200000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000")
    print("Test messgage send. Now sending invalid data")
    # test2.sendTestMessage('')
    # print("Invalid data send.")
except Exception as e:
    print("Test failed")
    print(e)
