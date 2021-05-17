"""
Filename: serviceorderhandler.py
Version name: 0.1, 2021-05-17
Short description: Module for handling the service request and creating responsens

(C) 2003-2021 IAS, Universitaet Stuttgart

"""


class ServiceOrderHandler(object):

    def __init__(self):
        self.tcpIdent = 0
        self.requestID = 0
        self.mClass = 0
        self.mNo = 0
        self.errorState = 0
        self.dataLength = 0
        self.resourceId = 0
        self.oNo = 0
        self.oPos = 0
        self.wpNo = 0
        self.opNo = 0
        self.bufNo = 0
        self.bufPos = 0
        self.carrierId = 0
        self.palletID = 0
        self.palletPos = 0
        self.pNo = 0
        self.stopperId = 0
        self.errorStepNo = 0
        self.stepNo = 0
        self.maxRecords = 0
        self.boxId = 0
        self.boxPos = 0
        self.mainOPos = 0
        self.beltNo = 0
        self.cNo = 0
        self.boxPNo = 0
        self.palletPNo = 0
        self.aux1Int = 0
        self.aux2Int = 0
        self.aux1DInt = 0
        self.aux2DInt = 0
        self.mainPNo = 0

    def createResponse(self, msg, ipAdress):
        pass

    def decodeMessage(self, msg):
        pass

    def getOutputParams(self):
        pass

    def encodeMessage(self):
        pass
