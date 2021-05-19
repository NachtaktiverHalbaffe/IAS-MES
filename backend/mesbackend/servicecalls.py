"""
Filename: servicecalls.py
Version name: 0.1, 2021-05-18
Short description: Module for handling the service calls. The buisness logic for each servicecall 
is handled here. Given on the servicecalls some output parameters are set

(C) 2003-2021 IAS, Universitaet Stuttgart

"""


class Servicecalls(object):

    def __init__(self):
        from .systemmonitoring import SystemMonitoring
        self.systemmonitoring = SystemMonitoring()

    def getFirstOpForRsc(self, obj):
        return

    def getOpForONoOPos(self, obj):
        return

    def opStart(self, obj):
        return

    def opReset(self, obj):
        return

    def opEnd(self, obj):
        return

    def getShuntForTarget(self, obj):
        return

    def getBufForBufNo(self, obj):
        return

    def getBufPos(self, obj):
        return

    def getToAGVBuf(self, obj):
        return
