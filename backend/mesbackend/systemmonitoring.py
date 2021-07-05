"""
Filename: systemmonitoring.py
Version name: 0.1, 2021-05-17
Short description: Module for monitoring the states of the plcs. Gets its information from PLCStateSocket and
ServiceOrderHandler

(C) 2003-2021 IAS, Universitaet Stuttgart

"""
from os import name
from django.apps import apps
import numpy as np
from django.utils import timezone

from .safteymonitoring import SafteyMonitoring


class SystemMonitoring(object):
    def __init__(self):
        self.ERROR_MSG_RESSID = "Invalid ressourceID"
        self.ERROR_MSG_SPSTYPE = "Invalid sps type"
        self.ERROR_MSG_STATUS = "Invalid status byte on ressource "
        self.ERROR_MSG_STATE = "Invalid busy bit on ressource "
        self.ERROR_MSG_MODE = "Invalid automatic oder default mode bit on ressource "
        self.ERROR_MSG_L0 = "Error of level 1 on ressource "
        self.ERROR_MSG_L1 = "Error of level 2 on ressource "
        self.ERROR_MSG_L2 = "warning on ressource "
        self.ERROR_MSG_DATA1 = "tried to update workingpiece with location "
        self.ERROR_MSG_DATA2 = "where no ressource exists"
        self.ERROR_MSG_LEN = "invalid length of message"


    # Gets cyclic messages from PLCStateSocket, decodes it to StatePLC and saves it. All neccessary inputs are validated.
    # @params:
    # msg: message from the TCP Socket
    # ipAdress: ip Adress from which the PLC send the Socket the message
    def decodeCyclicMessage(self, msg, ipAdress):
        if msg == "0000":
            return
        elif len(msg) != 8:
            SafteyMonitoring().decodeError(
                errorLevel=SafteyMonitoring().LEVEL_WARNING,
                errorCategory=SafteyMonitoring().CATEGORY_INPUT,
                msg=self.ERROR_MSG_LEN,
            )
            return
        else:
            # slice message to get sps type
            spsTypeStr = msg[4:6]
            spsType = int(spsTypeStr, 16)
            if spsType != 1 and spsType != 2:
                SafteyMonitoring().decodeError(
                    errorLevel=SafteyMonitoring().LEVEL_WARNING,
                    errorCategory=SafteyMonitoring().CATEGORY_INPUT,
                    msg=self.ERROR_MSG_SPSTYPE,
                )
                return

            # slice message to get raw ressourceId, needs to be decodes afterwards
            ressourceIDStr = msg[:4]
            ressourceId = self._getRessourceID(ressourceIDStr, spsType)

            # slice statusbyte to get status byte
            statusStr = msg[6:8]
            status = int(statusStr, 16)
            # convert to bit array
            statusbits = np.unpackbits(np.uint8(status))
            if len(statusbits) == 8:
                # assign status bits to parameter
                autoMode = statusbits[7]
                manualMode = statusbits[6]
                busy = statusbits[5]
                reset = statusbits[4]
                errorL0 = statusbits[3]
                errorL1 = statusbits[2]
                errorL2 = statusbits[1]
                mesMode = bool(statusbits[0])
            else:
                SafteyMonitoring().decodeError(
                    errorLevel=SafteyMonitoring().LEVEL_WARNING,
                    errorCategory=SafteyMonitoring().CATEGORY_INPUT,
                    msg=self.ERROR_MSG_STATUS + str(ressourceId),
                )
                return

            # save state and validate parameter if they arent already validated
            self._updateState(ressourceId, autoMode,
                              manualMode, busy, reset, mesMode, ipAdress)

            # check error bits
            if errorL0 == 1 and autoMode != 0 and manualMode != 0:
                SafteyMonitoring().decodeError(
                    errorLevel=SafteyMonitoring().LEVEL_ERROR,
                    errorCategory=SafteyMonitoring().CATEGORY_OPERATIONAL,
                    msg=self.ERROR_MSG_L0 + str(ressourceId),
                )
            elif errorL1 == 1 and autoMode != 0 and manualMode != 0:
                SafteyMonitoring().decodeError(
                    errorLevel=SafteyMonitoring().LEVEL_ERROR,
                    errorCategory=SafteyMonitoring().CATEGORY_OPERATIONAL,
                    msg=self.ERROR_MSG_L1 + str(ressourceId),
                )
            elif errorL2 == 1and autoMode != 0 and manualMode != 0:
                SafteyMonitoring().decodeError(
                    errorLevel=SafteyMonitoring().LEVEL_WARNING,
                    errorCategory=SafteyMonitoring().CATEGORY_OPERATIONAL,
                    msg=self.ERROR_MSG_L2 + str(ressourceId),
                )

    # Updates state of plc. Wether if a state of an plc already exists or not it gets updated or a new one created.
    # For every PLC there should only exist one state object. Some attributes are being validated too
    # @params: attributes to save which where decoded from the message
    def _updateState(
        self,
        ressourceId,
        autoMode,
        manualMode,
        busy,
        reset,
        mesMode,
        ipAdress,
    ):
        from mesapi.models import StatePLC
        mode = ""
        state = ""
        lastUpdate = timezone.now()

        # determine state of plc
        if busy == 1 and reset == 0:
            state = "busy"
        elif busy == 0 and reset == 0:
            state = "idle"
        elif busy == 0 and reset == 1:
            state = "ready"
        elif busy == 1 and reset == 1:
            state = "reset"
        else:
            SafteyMonitoring().decodeError(
                errorLevel=SafteyMonitoring().LEVEL_WARNING,
                errorCategory=SafteyMonitoring().CATEGORY_INPUT,
                msg=self.ERROR_MSG_STATE + str(ressourceId),
            )
            return

        # determine if plc is in auto or default mode
        if autoMode == 1 and manualMode == 0:
            mode = "auto"
        elif autoMode == 0 and manualMode == 1:
            mode = "default"
        elif autoMode == 0 and manualMode == 0:
            mode = "startup"
        else:
            SafteyMonitoring().decodeError(
                errorLevel=SafteyMonitoring().LEVEL_WARNING,
                errorCategory=SafteyMonitoring().CATEGORY_INPUT,
                msg=self.ERROR_MSG_MODE + str(ressourceId),
            )
            return

        if StatePLC.objects.filter(id=ressourceId).count() == 1:
            statePLC = StatePLC.objects.filter(id=ressourceId)
            statePLC.update(state=state)
            statePLC.update(mode=mode)
            statePLC.update(mesMode=mesMode)
            statePLC.update(lastUpdate=lastUpdate)
        else:
            statePLC = StatePLC(id=ressourceId, name='',
                                state=state, mode=mode, mesMode=mesMode, ipAdress=ipAdress[0], lastUpdate=lastUpdate)
            statePLC.save()

    # Decodes the ressourceId. Wether the PLC is big endian(Siemens) or little endian(Codesys) it needs
    # to be decoded diffrently
    # @params:
    # ressourceIDStr: String with ressourceId
    # spsType: type for sps (1= Codesys, 2 = Siemens)
    def _getRessourceID(self, ressourceIDStr, spsType):
        if spsType == 2:
            # sps is big endian
            ressourceIDStr = ressourceIDStr[:2] + ressourceIDStr[2:4]
            return int(ressourceIDStr, 16)
        elif spsType == 1:
            # sps is little endian
            ressourceIDStr = ressourceIDStr[2:4] + ressourceIDStr[:2]
            return int(ressourceIDStr, 16)
        else:
            # error
            SafteyMonitoring().decodeError(
                errorLevel=SafteyMonitoring().LEVEL_WARNING,
                errorCategory=SafteyMonitoring().CATEGORY_INPUT,
                msg=self.ERROR_MSG_RESSID,
            )
