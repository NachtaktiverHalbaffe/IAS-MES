"""
Filename: serviceorderhandler.py
Version name: 0.1, 2021-05-17
Short description: Module for handling the service request and creating responsens

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

from .safteymonitoring import SafteyMonitoring


class ServiceOrderHandler(object):

    def __init__(self):
        # Parameter for service calls
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
        self.serviceParams = []
        # Errorhandling
        self.safteyMonitoring = SafteyMonitoring()
        self.ERROR_ENCODING = "Couldn't encode message"

    def createResponse(self, msg, ipAdress):
        pass

    def decodeMessage(self, msg):
        pass

    def getOutputParams(self):
        pass

    # encodes message for PlcServiceOrderSocket in a format so it can be send
    # @params: Takes all the neccessary attributes of the Object and parses them
    def encodeMessage(self):
        if self.tcpIdent == 445:
            # String coding shortend
            return self._encodeStrFull()
        elif self.tcpIdent == 444:
            # String coding full
            return self._encodeStrFull()
        elif self.tcpIdent == '33:33:33:01:' or self.tcpIdent == "33:33:33:02:":
            # Binary coding
            return self._encodeBin()
        else:
            self.safteyMonitoring.decodeError(
                errorLevel=self.safteyMonitoring.LEVEL_ERROR,
                errorCategory=self.safteyMonitoring.CATEGORY_INPUT,
                msg=self.ERROR_ENCODING,
            )
            return

    # encodes message with full string format. Excluding the tcpident only the needed parameter are sent.
    # Format is parameter=value and each parameter is seperated with a ";"
    # @params: Takes all the neccessary attributes of the Object and parses them
    def _encodeStrFull(self):
        #Header
        msg = str(self.tcpIdent)
        if self.requestID != 0:
            msg += ";RequestID=" + str(self.requestID)
        if self.mClass != 0:
            msg += ";MClass=" + str(self.mClass)
        if self.mNo != 0:
            msg += ";MNo=" + str(self.mNo)
        if self.errorState != 0:
            msg += ";ErrorState=" + str(self.errorState)
        if self.dataLength != 0:
            msg += ";DataLength=" + str(self.dataLength)

        # standardparameter
        if self.resourceId != 0:
            msg += ";ResourceID=" + str(self.resourceId)
        if self.oNo != 0:
            msg += ";ONo=" + str(self.oNo)
        if self.oPos != 0:
            msg += ";OPos=" + str(self.oPos)
        if self.wpNo != 0:
            msg += ";WPNo=" + str(self.wpNo)
        if self.opNo != 0:
            msg += ";OpNo=" + str(self.opNo)
        if self.bufNo != 0:
            msg += ";BufNo=" + str(self.bufNo)
        if self.bufPos != 0:
            msg += ";BufPos=" + str(self.bufPos)
        if self.carrierId != 0:
            msg += ";CarrierID=" + str(self.carrierId)
        if self.palletID != 0:
            msg += ";PalletID=" + str(self.palletID)
        if self.palletPos != 0:
            msg += ";PalletPos=" + str(self.palletPos)
        if self.pNo != 0:
            msg += ";PNo=" + str(self.pNo)
        if self.stopperId != 0:
            msg += ";StopperID=" + str(self.stopperId)
        if self.errorStepNo != 0:
            msg += ";ErrorStepNo=" + str(self.errorStepNo)
        if self.stepNo != 0:
            msg += ";StepNo=" + str(self.stepNo)
        if self.maxRecords != 0:
            msg += ";MaxRecords=" + str(self.maxRecords)
        if self.boxId != 0:
            msg += ";BoxID=" + str(self.boxId)
        if self.boxPos != 0:
            msg += ";BoxPos=" + str(self.boxPNo)
        if self.mainOPos != 0:
            msg += ";MainOPos=" + str(self.mainOPos)
        if self.beltNo != 0:
            msg += ";BeltNo=" + str(self.beltNo)
        if self.cNo != 0:
            msg += ";CNo=" + str(self.cNo)
        if self.boxPNo != 0:
            msg += ";BoxPNo=" + str(self.boxPNo)
        if self.palletPNo != 0:
            msg += ";PalletPNo=" + str(self.palletPNo)
        if self.aux1Int != 0:
            msg += ";Aux1Int=" + str(self.aux1Int)
        if self.aux2Int != 0:
            msg += ";Aux2Int=" + str(self.aux2Int)
        if self.aux1DInt != 0:
            msg += ";Aux1DInt=" + str(self.aux1DInt)
        if self.aux2DInt != 0:
            msg += ";Aux2DInt=" + str(self.aux2DInt)
        if self.mainPNo != 0:
            msg += ";MainPNo=" + str(self.mainPNo)

        # service specific paramter. Each parameter is a 2 tuple with (parametername, parameter)
        for item in self.serviceParams:
            msg += ";" + item[0] + "=" + str(item[1])

        # evry message ends with <CR>
        msg += "<CR>"
        return msg

    # encodes message with shortemd string format. Like the binary format evry parameter is send in
    # the right order in ASCII and every parameter is seperated with a "<CR>"
    # @params: Takes all the neccessary attributes of the Object and parses them
    def _encodeStrShort(self):
        # header
        msg = "445<CR>"
        msg += str(self.requestID) + "<CR>"
        msg += str(self.mClass) + "<CR>"
        msg += str(self.mNo) + "<CR>"
        msg += str(self.errorState) + "<CR>"
        msg += str(self.dataLength) + "<CR>"

        # standard parameter
        msg += str(self.resourceId) + "<CR>"
        msg += str(self.oNo) + "<CR>"
        msg += str(self.oPos) + "<CR>"
        msg += str(self.wpNo) + "<CR>"
        msg += str(self.opNo) + "<CR>"
        msg += str(self.bufNo) + "<CR>"
        msg += str(self.bufPos) + "<CR>"
        msg += str(self.carrierId) + "<CR>"
        msg += str(self.palletID) + "<CR>"
        msg += str(self.palletPos) + "<CR>"
        msg += str(self.pNo) + "<CR>"
        msg += str(self.stopperId) + "<CR>"
        msg += str(self.errorStepNo) + "<CR>"
        msg += str(self.stepNo) + "<CR>"
        msg += str(self.maxRecords) + "<CR>"
        msg += str(self.boxId) + "<CR>"
        msg += str(self.boxPos) + "<CR>"
        msg += str(self.mainOPos) + "<CR>"
        msg += str(self.beltNo) + "<CR>"
        msg += str(self.cNo) + "<CR>"
        msg += str(self.boxPNo) + "<CR>"
        msg += str(self.palletPNo) + "<CR>"
        msg += str(self.aux1Int) + "<CR>"
        msg += str(self.aux2Int) + "<CR>"
        msg += str(self.aux1DInt) + "<CR>"
        msg += str(self.aux2DInt) + "<CR>"
        msg += str(self.mainPNo) + "<CR>"

        # service-specific parameter
        for item in self.serviceParams:
            msg += str(item) + "<CR>"
        return msg

    def _encodeBin(self):
        # Header
        msg = str(self.tcpIdent)
        msg += self._parseEndian(self.requestID, False)
        msg += self._parseEndian(self.mClass, False)
        msg += self._parseEndian(self.mNo, False)
        msg += self._parseEndian(self.errorState, False)
        msg += self._parseEndian(self.dataLength, False)

        # standardparameter
        msg += self._parseEndian(self.resourceId, False)
        msg += self._parseEndian(self.oNo, True)
        msg += self._parseEndian(self.oPos, False)
        msg += self._parseEndian(self.wpNo, False)
        msg += self._parseEndian(self.opNo, False)
        msg += self._parseEndian(self.bufNo, False)
        msg += self._parseEndian(self.bufPos, False)
        msg += self._parseEndian(self.carrierId, False)
        msg += self._parseEndian(self.palletID, False)
        msg += self._parseEndian(self.palletPos, False)
        msg += self._parseEndian(self.pNo, True)
        msg += self._parseEndian(self.stopperId, False)
        msg += self._parseEndian(self.errorStepNo, False)
        msg += self._parseEndian(self.stepNo, False)
        msg += self._parseEndian(self.maxRecords, False)
        msg += self._parseEndian(self.boxId, False)
        msg += self._parseEndian(self.boxPos, False)
        msg += self._parseEndian(self.mainOPos, False)
        msg += self._parseEndian(self.beltNo, False)
        msg += self._parseEndian(self.cNo, True)
        msg += self._parseEndian(self.boxPNo, True)
        msg += self._parseEndian(self.palletPNo, True)
        msg += self._parseEndian(self.aux1Int, False)
        msg += self._parseEndian(self.aux2Int, False)
        msg += self._parseEndian(self.aux1DInt, True)
        msg += self._parseEndian(self.aux2DInt, True)
        msg += self._parseEndian(self.mainPNo, True)
        # standardparameter bytes reserved
        for item in range(44):
            msg += "00:"

        # servicespecific parameter
        for i in range(len(self.serviceParams)):
            if i != len(self.serviceParams):
                msg += self._parseEndian(self.serviceParams[i], False) + ":"
            else:
                msg += self._parseEndian(self.serviceParams[i], False)
                # cut of last ":"
                msg = msg[:len(msg)-1]

        return msg

    # parses a number to hex in the binary format
    # @params:
    # number: number to parse
    # isInt32: if number is int32 (true) or int16(false)
    def _parseEndian(self, number, isInt32):
        if isInt32:
            hex = format(number, "08x")
        else:
            hex = format(number, "04x")

        binArray = [hex[i:i+2] for i in range(0, len(hex), 2)]
        binStr = ""

        if self.tcpIdent == "33:33:33:02:":
            for i in range(0, len(binArray), 1):
                binStr += binArray[i] + ":"
        elif self.tcpIdent == "33:33:33:01:":
            for i in range(len(binArray)-1, -1, -1):
                binStr += binArray[i] + ":"

        return binStr
