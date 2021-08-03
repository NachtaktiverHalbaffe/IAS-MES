"""
Filename: servicecalls.py
Version name: 1.0, 2021-07-10
Short description: Module for handling the service calls. The buisness logic for each servicecall
is handled here. Given on the servicecalls some output parameters are set

(C) 2003-2021 IAS, Universitaet Stuttgart
"""

from mesapi.models import AssignedOrder, Buffer, Customer, Setting, StatePLC, StateVisualisationUnit, WorkingPlan, WorkingStep, StateWorkingPiece
import logging
import requests
from threading import Thread


class Servicecalls(object):

    def __init__(self):
        from .safteymonitoring import SafteyMonitoring
        self.safteymonitoring = SafteyMonitoring()
        # setup logging
        log_formatter = logging.Formatter('[%(asctime)s ] %(message)s')
        # handler for logging to file
        file_handler = logging.FileHandler("orders.log")
        file_handler.setFormatter(log_formatter)
        file_handler.setLevel(logging.INFO)
        # handler for logging to console
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(log_formatter)
        stream_handler.setLevel(logging.INFO)
        # setup logger
        self.logger = logging.getLogger("servicecalls")
        self.logger.setLevel(logging.INFO)
        # add logger handler to logger
        self.logger.handlers = []
        self.logger.addHandler(stream_handler)
        self.logger.addHandler(file_handler)

    # get first unfinished operation for resource
    # @param:
    #   obj: instance of serviceorderhandler
    # @return:
    #   updated instance of serviceorderhanlder with updated output params
    def getFirstOpForRsc(self, obj):
        # input params
        resourceId = obj.resourceId
        stopperId = obj.stopperId
        # avoid spam in logs because resources 1+2 requests this often
        if resourceId > 2:
            self.logger.info(
                "[SERVICEORDERHANDLER] Request GetFirstOpForRsc for resource " + str(resourceId))

        # Load current orders and  and determine if the ressource has a working step in it
        currentOrder = AssignedOrder.objects.all()
        for order in currentOrder:
            workingPlan = order.assigendWorkingPlan
            if workingPlan != None:
                workingsteps = workingPlan.workingSteps.all().filter(assignedToUnit=resourceId)
                status = order.getStatus()
                if workingsteps.count() != 0:
                    for step in workingsteps:
                        stepsToCheck = workingPlan.workingSteps.all()
                        # search position in workingsteps
                        for i in range(len(status)):
                            # only start operation if it isnt already finished
                            if status[i] == 0:
                                if stepsToCheck[i].id == step.id:
                                    self.logger.info(
                                        "[GETFIRSTOPFORRSC] Found active order for resource " + str(resourceId))
                                    # set general output parameter
                                    obj.resourceId = resourceId
                                    obj.stepNo = step.stepNo
                                    obj.oNo = order.orderNo
                                    obj.oPos = order.orderPos
                                    obj.wpNo = workingPlan.workingPlanNo
                                    obj.opNo = step.operationNo
                                    if order.customer != None:
                                        obj.cNo = order.customer.customerNo
                                    obj.mainOPos = order.mainOrderPos
                                    obj.errorStepNo = 0
                                    workingPiece = order.assignedWorkingPiece
                                    obj.pNo = workingPiece.partNo
                                    # set output params specific to operation
                                    if step.operationNo == 210 or step.operationNo == 211:
                                        obj.dataLength = 12
                                        bufPos = 0
                                        for j in range(1, 30):
                                            # no Stateworkingpiece with that storagelocation => storagelocation must be emtpy
                                            if StateWorkingPiece.objects.filter(storageLocation=j).count() == 0:
                                                bufPos = j
                                        if stopperId == 1:
                                            # store from stopper 1
                                            obj.stopperId = 1
                                            obj.opNo = 210
                                            # serviceparams[constant, position in storage, part number], each param has 2 bytes, so each param is padded with a 0
                                            obj.serviceParams = [
                                                0, bufPos, 0, 90, 0, obj.pNo]
                                        elif stopperId == 2:
                                            # store from stopper 2
                                            obj.stopperId = 2
                                            obj.opNo = 211
                                            obj.serviceParams = [
                                                0, bufPos, 0, 91, 0, obj.pNo]
                                        # update mes data
                                        workingPiece.storageLocation = obj.bufPos
                                        workingPiece.carrierId = 0
                                    # operation is manual work
                                    elif step.operationNo == 510:
                                        obj.stopperId = 0
                                        obj.serviceParams = [0, 1, 0, 1,
                                                             0, 25, 0, 0, 0, 0, 0, 0, 0, 0]
                                        obj.dataLength = 28
                                    # operation is delay
                                    elif step.operationNo == 1110:
                                        obj.stopperId = 0
                                        delayTime = 5
                                        obj.dataLength = 2
                                        # serviceparam[seconds], seconds = seconds which the carrier will wait,
                                        # param consists of two bytes, so param is padded with leading zero
                                        obj.serviceParams = [0, delayTime]
                                    # update mes data
                                    workingPiece.location = resourceId
                                    workingPiece.save()
                                    return obj
                                else:
                                    obj.stopperId = 0
                                    obj.resourceId = 0
                                    obj.serviceParams = [0, 0]
                                    obj.dataLength = 4
                                    break
                    obj.resourceId = 0
                    obj.serviceParams = [0, 0]
                    obj.dataLength = 4
                    obj.stopperId = 0
            else:
                obj.resourceId = 0
                obj.serviceParams = [0, 0]
                obj.dataLength = 4
                obj.stopperId = 0
        return obj

    # get next operation for ONo and OPos
    # @param:
    #   obj: instance of serviceorderhandler
    # @return:
    #   updated instance of serviceorderhanlder with updated output params
    def getOpForONoOPos(self, obj):
        # input params
        requestId = obj.requestID
        stopperId = obj.stopperId
        oNo = obj.oNo
        oPos = obj.oPos
        self.logger.info(
            "[SERVICEORDERHANDLER] Request GetOpForONoOPos for resource " + str(requestId) + " and ONo " + str(oNo) + " and OPos " + str(oPos))
        obj.stopperId = 0
        # Load current orders and search if theres a order according to orderNo and Opos
        currentOrder = AssignedOrder.objects.filter(
            orderNo=oNo).filter(orderPos=oPos)
        if currentOrder.count() == 1:
            currentOrder = currentOrder.first()
            workingPlan = currentOrder.assigendWorkingPlan
            workingsteps = workingPlan.workingSteps.all()
            status = currentOrder.getStatus()
            # get assigned workingpiece and update location where piece is located
            workingPiece = StateWorkingPiece.objects.filter(
                id=currentOrder.assignedWorkingPiece.id).first()
            workingPiece.location = requestId
            workingPiece.save()
            partNo = workingPiece.partNo
            for i in range(len(status)):
                # find first step which isnt executed yet
                if status[i] == 0:
                    self.logger.info(
                        "[GETOPFORONOOPOS] Found active order for ordernumber " + str(oNo)+" for resource " + str(requestId))
                    # set general output parameter
                    obj.oNo = oNo
                    obj.oPos = oPos
                    obj.stepNo = workingsteps[i].stepNo
                    obj.resourceId = workingsteps[i].assignedToUnit
                    obj.wpNo = workingPlan.workingPlanNo
                    obj.opNo = workingsteps[i].operationNo
                    if currentOrder.customer != None:
                        obj.cNo = currentOrder.customer.customerNo
                    else:
                        obj.cNo = 0
                    obj.mainOPos = currentOrder.mainOrderPos
                    obj.errorStepNo = 0
                    obj.pNo = 25  # 25= pallet, 31 = carrier
                    if currentOrder.assignedWorkingPiece.carrierId != None:
                        obj.carrierId = currentOrder.assignedWorkingPiece.carrierId
                    # set output params specific to operation
                    # operation is store a part
                    if workingsteps[i].operationNo == 210 or workingsteps[i].operationNo == 211:
                        # set output params
                        obj.dataLength = 12
                        bufPos = 0
                        for j in range(1, 30):
                            # no Stateworkingpiece with that storagelocation => storagelocation must be emtpy
                            if StateWorkingPiece.objects.filter(storageLocation=j).count() == 0:
                                bufPos = j
                        if stopperId == 1:
                            # store from stopper 1
                            obj.stopperId = 1
                            obj.opNo = 210
                            # serviceparams[constant, position in storage, part number], each param has 2 bytes, so each param is padded with a 0
                            obj.serviceParams = [
                                0, 90, 0, bufPos, 0, partNo]
                        elif stopperId == 2:
                            # store from stopper 2
                            obj.stopperId = 2
                            obj.opNo = 211
                            obj.serviceParams = [
                                0, 91, 0, bufPos, 0, partNo]
                        # update mes data
                        workingPiece.storageLocation = bufPos
                        workingPiece.carrierId = 0
                        workingPiece.save()
                    if obj.opNo == 212 or obj.opNo == 213:
                        bufPos = currentOrder.assignedWorkingPiece.storageLocation
                        #obj.bufNo = 1
                        #obj.bufPos = bufPos
                        if stopperId == 1:
                            obj.opNo = 212
                            obj.stopperId = 1
                            # serviceparams[constant, position in storage, part number], each param has 2 bytes, so each param is padded with a 0
                            obj.serviceParams = [
                                0, bufPos, 0, 90, 0, partNo]
                        elif stopperId == 2:
                            obj.opNo = 213
                            obj.stopperId = 2
                            obj.serviceParams = [
                                0, 91, 0, bufPos, 0, partNo]
                        # update mes data
                        workingPiece.storageLocation = 0
                        workingPiece.save()
                    # operation is manual work
                    elif workingsteps[i].operationNo == 510:
                        obj.serviceParams = [0, 1, 0, 1,
                                             0, partNo, 0, 0, 0, 0, 0, 0, 0, 0]
                        obj.dataLength = 28
                    return obj
                # no operation found
                else:
                    obj.oNo = 0
                    obj.oPos = 0
                    obj.stopperId = 0
        return obj

    # get operation that is for this Stopper and the PNo is available
    # @param:
    #   obj: instance of serviceorderhandler
    # @return:
    #   updated instance of serviceorderhanlder with updated output params
    def getOpForASRS(self, obj):
        # input params
        resourceId = obj.resourceId
        stopperId = obj.stopperId
        currentOrder = AssignedOrder.objects.all()
        for order in currentOrder:
            workingPlan = order.assigendWorkingPlan
            workingsteps = workingPlan.workingSteps.all()
            status = order.getStatus()
            for i in range(len(status)):
                # search for first unfinished step
                if status[i] == 0:
                    # check if step is for ASRS and if asrs isnt already executing this task
                    if workingsteps[i].assignedToUnit == resourceId and StatePLC.objects.filter(id=1).state == "idle":
                        self.logger.info(
                            "[GETOPFORASRS] Found active order for ASRS")
                        # set general output parameter
                        obj.oNo = order.orderNo
                        obj.oPos = order.orderPos
                        obj.stepNo = workingsteps[i].stepNo
                        obj.resourceId = workingsteps[i].assignedToUnit
                        obj.wpNo = workingPlan.workingPlanNo
                        obj.opNo = workingsteps[i].operationNo
                        obj.bufNo = 1
                        if order.customer != None:
                            obj.cNo = order.customer.customerNo
                        obj.mainOPos = order.mainOrderPos
                        obj.errorStepNo = 0
                        obj.pNo = 25  # 25= pallet, 31 = carrier
                        if order.assignedWorkingPiece.carrierId != None:
                            obj.carrierId = order.assignedWorkingPiece.carrierId
                        else:
                            obj.carrierId = 0
                        obj.dataLength = 12
                        obj.bufPos = order.assignedWorkingPiece.storageLocation
                        workingPiece = order.assignedWorkingPiece
                        partNo = workingPiece.partNo
                        # set output parameter specific to operation
                        # operation is unstore a part
                        if obj.opNo == 212 or obj.opNo == 213:
                            obj.dataLength = 12
                            if stopperId == 1:
                                obj.opNo = 212
                                obj.stopperId = 1
                                # serviceparams[constant, position in storage, part number], each param has 2 bytes, so each param is padded with a 0
                                obj.serviceParams = [
                                    0, obj.bufPos, 0, 90, 0, partNo]
                            elif stopperId == 2:
                                obj.opNo = 213
                                obj.stopperId = 2
                                obj.serviceParams = [
                                    0, obj.bufPos, 0, 91, 0, partNo]
                                self.logger.info(str(obj.serviceParams))
                            # update mes data
                            workingPiece.storageLocation = 0
                            workingPiece.save()
                            return obj
                    else:
                        obj.stopperId = 0
                        obj.serviceParams = [0, 0]
                        obj.dataLength = 4
                        return obj
                    break
                else:
                    # no active order for asrs
                    obj.stopperId = 0
        return obj

    # get the free string for the actual order which represents a url which is displayed on HMI
    # @param:
    #   obj: instance of serviceorderhandler
    # @return:
    #   updated instance of serviceorderhanlder with updated output params
    def getFreeString(self, obj):
        # input params
        requestId = obj.requestID
        oNo = obj.oNo
        oPos = obj.oPos
        order = AssignedOrder.objects.all().filter(
            orderNo=oNo).filter(orderPos=oPos)
        freeString = ""
        # get params for string
        if order.count() == 1:
            order = order.first()
            step = order.assigendWorkingPlan.workingSteps.filter(
                assignedToUnit=requestId).first()
            obj.stepNo = str(step.stepNo)
            obj.stepNo = step.stepNo
        # parse freestring
            freeString = "http://129.69.102.129/I4.0/mes4/EN/mes4.php?content=manual&OpNo=510&Workpiece=3&Action=4&PNo=25"
            # freeString = "http://129.69.102.129:8080/"  # page from frontend

        serviceParams = []
        # max length of string
        serviceParams.append(254)
        # actual length of string
        serviceParams.append(len(freeString))
        for i in range(serviceParams[1]):
            serviceParams.append(ord(freeString[i]))
        # pad serviceparams to full length with 0
        while len(serviceParams) != 256:
            serviceParams.append(0)

        obj.serviceParams = serviceParams
        obj.dataLength = 256
        return obj

    # set parameters on runtime (not needed for MES, but needed for PLC as response)
    # @param:
    #   obj: instance of serviceorderhandler
    # @return:
    #   updated instance of serviceorderhanlder with updated output params
    def setPar(self, obj):
        # input params
        requestId = obj.requestID
        oNo = obj.oNo
        oPos = obj.oPos
        stepNo = obj.stepNo
        # Load current orders and search if theres a order according to orderNo and Opos
        currentOrder = AssignedOrder.objects.all()
        for order in currentOrder:
            if order.orderNo == oNo and order.orderPos == oPos:
                self.logger.info("[SETPAR] Found order to set parameter")
                break
        obj.oNo = 0
        obj.oPos = 0
        obj.stepNo = 0
        obj.dataLength = 0
        obj.resourceId = 0
        obj.serviceParams = []
        return obj

    # operation start
    # @param:
    #   obj: instance of serviceorderhandler
    # @return:
    #   updated instance of serviceorderhanlder with updated output params
    def opStart(self, obj):
        # input params
        requestId = obj.requestID
        oNo = obj.oNo
        oPos = obj.oPos
        # Load current orders and search if theres a order according to orderNo and Opos
        currentOrder = AssignedOrder.objects.all().filter(
            orderNo=oNo).filter(orderPos=oPos)
        if currentOrder.count() == 1:
            self.logger.info(
                "[OPSTART] Operation  started on resource " + str(requestId))
            # set output parameter
            obj.oNo = 0
            obj.oPos = 0
            # update mes data
            workingpiece = currentOrder.first().assignedWorkingPiece
            workingpiece.location = requestId
            workingpiece.save()
        return obj

    # reset start operation
    # @param:
    #   obj: instance of serviceorderhandler
    # @return:
    #   updated instance of serviceorderhanlder with updated output params
    def opReset(self, obj):
        # input parameter
        oNo = obj.oNo
        oPos = obj.oPos
        requestId = obj.requestID
        order = AssignedOrder.objects.filter(
            orderNo=oNo).filter(orderPos=oPos)
        if order.count() != 0:
            order = order.first()
            workingsteps = order.assigendWorkingPlan.workingSteps.filter(
                assignedToUnit=requestId)
            status = order.getStatus()
            for i in range(len(status)):
                if workingsteps[i].assignedToUnit == requestId:
                    # update status of task to unfinished if it is marked as finished
                    if status[i] == 1:
                        status[i] = 0
                        order.setStatus(status)
                        order.save()
                        self.logger.info(
                            "[OPRESET] Reset operation  on resource " + str(requestId))
        # set output parameter
        obj.oNo = 0
        obj.oPos = 0
        return obj

    # operation end. Sends next operation to resource to write on NFC tag
    # @param:
    #   obj: instance of serviceorderhandler
    # @return:
    #   updated instance of serviceorderhanlder with updated output params
    def opEnd(self, obj):
        # get input parameter
        requestId = obj.requestID
        carrierId = obj.carrierId
        oNo = obj.oNo
        oPos = obj.oPos
        self.logger.info("[OPEND] Requested OpEnd for oNo: " +
                         str(oNo) + " and oPos " + str(oPos))
        # Find corresponding order
        # request send valid oNo and oPos so it can be searched
        currentOrder = AssignedOrder.objects.all().filter(
            orderNo=oNo).filter(orderPos=oPos)
        if currentOrder.count() != 0:
            order = currentOrder.first()
            workingPlan = order.assigendWorkingPlan
            workingsteps = workingPlan.workingSteps.all()
            # set general output parameter
            obj.oNo = order.orderNo
            obj.oPos = order.orderPos
            obj.wpNo = workingPlan.workingPlanNo
            obj.mainOPos = order.mainOrderPos
            obj.errorStepNo = 0
            obj.pNo = 25  # 25= pallet, 31 = carrier
            status = order.getStatus()
            if order.customer != None:
                obj.cNo = order.customer.customerNo
            else:
                obj.cNo = 0
            for i in range(len(status)):
                # find first unfinished step in list
                if status[i] == 0:
                    # set output parameters
                    # Write NFC tags, data for NFC tag can be manipulated here
                    stateVisualisationUnit = StateVisualisationUnit.objects.all().filter(
                        boundToRessource=requestId)
                    # check if visualisation unit is mounted on resource
                    if stateVisualisationUnit.count() != 0:
                        # only check if resource is branch
                        stateVisualisationUnit = stateVisualisationUnit.first()
                        # visualisationunit finished task => write next step of workingplan on rfid,
                        if stateVisualisationUnit.state == "finished" or stateVisualisationUnit.state == "idle" and requestId > 1 and requestId < 7:
                            if i+1 < len(status):
                                obj.stepNo = workingsteps[i+1].stepNo
                                obj.resourceId = workingsteps[i +
                                                              1].assignedToUnit
                                obj.opNo = workingsteps[i+1].operationNo
                                status[i] = 1
                                order.setStatus(status)
                                order.save()
                                Thread(target=self._sendVisualisationTask, args=[
                                       oNo, oPos, obj.resourceId, obj.stepNo]).start()
                                break
                        # visualisationunit hasnt finished => write current task again to repeat operation on PLC
                        elif stateVisualisationUnit.state == "playing" or stateVisualisationUnit.state == "waiting" and requestId > 1 and requestId < 7:
                            self.logger.info(
                                "[OPEND] Attached visualisationunit hasnt finished. Write same step again on RFID to repeat operation")
                            obj.stepNo = workingsteps[i].stepNo
                            obj.resourceId = workingsteps[i].assignedToUnit
                            obj.opNo = workingsteps[i].operationNo
                            break
                    # no visualisation unit mounted on resource
                    else:
                        # there is a next steo
                        if i+1 < len(status):
                            obj.stepNo = workingsteps[i+1].stepNo
                            obj.resourceId = workingsteps[i+1].assignedToUnit
                            obj.opNo = workingsteps[i+1].operationNo
                            status[i] = 1
                            order.setStatus(status)
                            order.save()
                            Thread(target=self._sendVisualisationTask, args=[
                                   oNo, oPos, obj.resourceId, obj.stepNo]).start()
                            break
                        # order finished
                        else:
                            obj.resourceId = 0
                            obj.oNo = 0
                            obj.oPos = 0
                            obj.wpNo = 0
                            obj.opNo = 0
                            obj.pNo = 0
                            obj.stepNo = 0
                            status[i] = 1
                            order.setStatus(status)
                            order.save()
                            # all steps in workingplan are complete => delete order
                            if not 0 in status:
                                order.delete()
                            break

                    self.logger.info("[OPEND] Operation on resource " +
                                     str(requestId) + " ended. Writing next operation on RFID with ONo: " + str(obj.oNo) + " and OPos " + str(obj.oPos))
                    # update data
                    workingpiece = StateWorkingPiece.objects.filter(
                        id=order.assignedWorkingPiece.id)
                    workingpiece.update(carrierId=carrierId)
                    workingpiece.update(location=requestId)
        # no active order for corresponding ordernumber and orderposition
        else:
            obj.oNo = 0
            obj.oPos = 0
        return obj

    # get shunt for target resource
    # @param:
    #   obj: instance of serviceorderhandler
    # @return:
    #   updated instance of serviceorderhanlder with updated output params
    def getShuntForTarget(self, obj):
        # input params
        requestID = obj.requestID
        sourceId = obj.serviceParams[0]
        targetId = obj.serviceParams[2]
        self.logger.info("[SERVICEORDERHANDLER] Requested GetShuntForTarget for resource " +
                         str(requestID))
        # set output parameter
        obj.dataLength = 2

        # workingpiece is on brqanch 2 and has to go to storage
        if targetId == 1 and requestID == 2:
            self.logger.info("[GETSHUNTFORTARGET] Branch for resource " +
                             str(requestID) + " is set to straight forward")
            # serviceparams[position] with position = 1 straight forward and position=2 to bufOut
            obj.serviceParams = [1]
        # workingpiece is on branch 3 or 4 which are connected and has to stay on the two of them
        elif (targetId == 3 and sourceId == 4) or sourceId == 3 or (targetId == 4 and sourceId == 3):
            self.logger.info("[GETSHUNTFORTARGET] Branch for resource " +
                             str(requestID) + " is set to straight forward")
            # serviceparams[position] with position = 1 straight forward and position=2 to bufOut
            obj.serviceParams = [1]
        # workingpiece has to leave resource
        elif targetId != requestID:
            self.logger.info("[GETSHUNTFORTARGET] Branch for resource " +
                             str(requestID) + " is set to buffer out")
            # serviceparams[position] with position = 1 straight forward and position=2 to bufOut
            obj.serviceParams = [2]
        # workingpiece has to stay on the resource
        else:
            self.logger.info("[GETSHUNTFORTARGET] Branch for resource " +
                             str(requestID) + " is set to straight forward")
            # serviceparams[position] with position = 1 straight forward and position=2 to bufOut
            obj.serviceParams = [1]

        return obj

    # get all BufPos for defined BufNo and resource
    # @param:
    #   obj: instance of serviceorderhandler
    # @return:
    #   updated instance of serviceorderhanlder with updated output params
    def getBufForBufNo(self, obj):
        # get input parameter
        resourceId = obj.resourceId
        bufNo = obj.bufNo

        # get output parameter
        plc = StatePLC.objects.all().filter(id=resourceId).first()
        plcBuf = plc.buffer
        obj.palletID = 0
        # PLC is robotino or branch
        if resourceId != 1:
            bufPos = 0
            oPos = 0
            oNo = 0
            pNo = 0
            if bufNo == 1:
                if plcBuf.bufOutONo != 0:
                    bufPos = 1
                    oNo = plcBuf.bufOutONo
                    oPos = plcBuf.bufOutOPos
                    pNo = 25
                else:
                    obj.pNo = 0
            elif bufNo == 2:
                if plcBuf.bufInONo != 0:
                    bufPos = 1
                    oNo = plcBuf.bufInONo
                    oPos = plcBuf.bufInOPos
                    pNo = 25
                    pNo = 25
                else:
                    obj.pNo = 0

        self.logger.info(
            "[GETBUFFORBUFNO] Returned buffer to resource " + str(resourceId))
        serviceParams = [bufPos, oPos, oNo, pNo, 0]
        obj.serviceParams = serviceParams
        return obj

    # get buffer of defined BufPos
    # @param:
    #   obj: instance of serviceorderhandler
    # @return:
    #   updated instance of serviceorderhanlder with updated output params
    def getBufPos(self, obj):
        # get input parameter
        resourceId = obj.resourceId
        bufNo = obj.bufNo
        bufPos = obj. bufPos
        self.logger.info(
            "[SERVICEORDERHANDLER] Requested buffer of " + str(resourceId))
        # get output parameter
        plc = StatePLC.objects.all().filter(id=resourceId)
        if plc.count() == 1:
            plc = plc.first()
            plcBuf = plc.buffer
            obj.palletID = 0
            obj.boxId = 0
            # PLC is storage
            if resourceId == 1:
                if bufNo == 1:
                    obj.oNo = 0
                    obj.oPos = 0
                    workingPiece = StateWorkingPiece.objects.filter(
                        storageLocation=bufPos)
                    if workingPiece.count() == 1:
                        obj.pNo = 25
                        obj.boxPNo = 25
                    else:
                        obj.pNo = 0
                        obj.boxPNo = 0
            # PLC is robotino or branch
            elif resourceId != 1:
                if bufNo == 1 and bufPos == 1:
                    if plcBuf.bufOutONo != 0:
                        obj.pNo = 25
                    else:
                        obj.pNo = 0
                    obj.oNo = plcBuf.bufOutONo
                    obj.oPos = plcBuf.bufOutOPos

                elif bufNo == 2 and bufPos == 1:
                    if plcBuf.bufInONo != 0:
                        obj.pNo = 25
                    else:
                        obj.pNo = 0
                    obj.oNo = plcBuf.bufInONo
                    obj.oPos = plcBuf.bufOutOPos
        # no buffer found
        else:
            obj.pNo = 0
            obj.oNo = 0
            obj.oPos = 0
            obj.palletID = 0
            obj.boxId = 0
        self.logger.info(
            "[GETBUFPOS] Returned buffer of resource " + str(resourceId))
        return obj

    # get buffer from the docked AGV
    # @param:
    #   obj: instance of serviceorderhandler
    # @return:
    #   updated instance of serviceorderhanlder with updated output params
    def getBufDockedAgv(self, obj):
        # get input params
        requestId = obj.requestID
        # get buffer of robotino
        robotino = StatePLC.objects.filter(dockedAt=requestId)
        buffer = None
        if robotino.count() == 1:
            buffer = robotino.first().buffer
            obj.resourceId = robotino.first().id
        # hasnt fpund robotino via the docketAt position
        else:
            plcs = StatePLC.objects.all()
            for resource in plcs:
                if resource.id >= 6:
                    # robotino is busy => has to be in docking process
                    if resource.state == "busy":
                        buffer = resource.buffer
                        obj.resourceId = resource.id
                        break

        # set output params
        if buffer != None:
            obj.oNo = buffer.bufOutONo
            obj.oPos = buffer.bufOutOPos
            if obj.oNo != 0:
                obj.bufNo = 1
                obj.bufPos = 1
                obj.pNo = 25
            else:
                obj.bufNo = 0
                obj.bufPos = 0
                obj.pNo = 0
        else:
            obj.bufNo = 0
            obj.bufPos = 0
            obj.pNo = 0

        # update buffer
        buffResource = Buffer.objects.filter(resourceId=requestId)
        if buffResource.count() == 1:
            if obj.oNo != 0:
                # if resource gets buffer from robotino, then move buffer from robotino to resource bufferIn.
                # If resource gives buffer to robotino, then the bufferupdate is
                # done by moveBuffer()
                buffResource.update(bufInONo=obj.oNo)
                buffResource.update(bufInOPos=obj.oPos)
        if obj.oNo != 0:
            # if resource gets buffer from robotino, then delete buffer.
            # If resource gives buffer to robotino, then the bufferupdate is
            # done by moveBuffer()
            buffer.bufOutONo = 0
            buffer.bufOutOPos = 0
            buffer.save()

        self.logger.info(
            "[GETBUFDOCKEDAGV] Returned buffer of docked robotino " + str(obj.resourceId) + " to resource " + str(requestId))
        return obj

    # move a buffer from source to target (for buffer and FIFO)
    # @param:
    #   obj: instance of serviceorderhandler
    # @return:
    #   updated instance of serviceorderhanlder with updated output params
    def moveBuf(self, obj):
        self.logger.info("[SERVICEORDERHANDLER] Request MoveBuf")
        # input parameter
        inputParameter = obj.serviceParams
        # get buffer from request which should be moved
        oldId = inputParameter[0]
        oldBufNo = inputParameter[1]
        oldBufPos = inputParameter[2]
        newId = inputParameter[3]
        newBufNo = inputParameter[4]
        newBufPos = inputParameter[5]

        # update buffer
        originPlc = StatePLC.objects.all().filter(id=oldId)
        targetPlc = StatePLC.objects.all().filter(id=newId)
        if originPlc.count() == 1 and targetPlc.count() == 1:
            # get buffer
            oldbuffer = Buffer.objects.filter(resourceId=oldId)
            targetbuffer = Buffer.objects.filter(resourceId=newId)
            oNo = oldbuffer.first().bufOutONo
            oPos = oldbuffer.first().bufOutOPos
            if newBufNo == 1:
                targetbuffer.update(bufOutONo=oNo)
                targetbuffer.update(bufOutOPos=oPos)
            elif newBufNo == 2:
                targetbuffer.update(bufInONo=oNo)
                targetbuffer.update(bufInOPos=oPos)
        # update origin buffer
            # update source buffer (only if old buffer isnt robotino)
            if oldId < 7:
                if oldBufNo == 1:
                    oldbuffer.update(bufOutONo=0)
                    oldbuffer.update(bufOutOPos=0)
                elif oldBufNo == 2:
                    oldbuffer.update(bufInONo=0)
                    oldbuffer.update(bufInOPos=0)

        # update location of workingpiece
        StateWorkingPiece.objects.filter(location=oldId).update(location=newId)
        self.logger.info("[MOVEBUF] Moved buffer from resource " +
                         str(oldId) + " to resource " + str(newId))
        # set output parameter
        obj.serviceParams = []
        obj.dataLength = 0
        return obj

    # write in buffer; Aux1Int = Quantity of a stack buffer
    # @param:
    #   obj: instance of serviceorderhandler
    # @return:
    #   updated instance of serviceorderhanlder with updated output params
    def setBufPos(self, obj):
        # get input parameter
        requestId = obj.requestID
        resourceId = obj.resourceId
        bufNo = obj.bufNo
        bufPos = obj.bufPos
        partNo = obj.pNo
        oNo = obj.oNo
        oPos = obj.oPos
        self.logger.info(
            "[SERVICEORDERHANDLER] Request SetBufPos for resource " + str(resourceId))
        if oNo != 0 and partNo == 0:
            partNo = 25
        # update buffer of plc
        statePlc = StatePLC.objects.all().filter(id=resourceId)
        if statePlc.count() == 1:
            # PLC isnt storage
            if resourceId != 1:
                statePlc = statePlc.first()
                buffer = Buffer.objects.filter(resourceId=statePlc.id)
                if bufNo == 1:
                    if oNo != 0:
                        buffer.update(bufOutONo=oNo)
                        buffer.update(bufOutOPos=oPos)
                    elif partNo == 0:
                        buffer.update(bufOutONo=0)
                        buffer.update(bufOutOPos=0)
                elif bufNo == 2:
                    if partNo != 0:
                        buffer.update(bufInONo=oNo)
                        buffer.update(bufInOPos=oPos)
                    elif partNo == 0:
                        buffer.update(bufInONo=0)
                        buffer.update(bufInOPos=0)
            # PLC is storage
            elif resourceId == 1:
                if bufNo == 1:
                    # updating storageposition of workingpiece is done
                    # in getOpForONoOPos or getOpForASRS in the corresponding store/
                    # unstore
                    pass

        # return all output parameter as 0 because resource exspects this response
        obj.resourceId = 0
        obj.bufNo = 0
        obj.bufPos = 0
        obj.pNo = 0
        obj.oNo = 0
        obj.oPos = 0
        obj.palletID = 0
        obj.boxId = 0
        self.logger.info("[SETBUFPOS] Buffer for resource " +
                         str(resourceId) + " set")
        return obj

    # delete all positions of a defined buffer
    # @param:
    #   obj: instance of serviceorderhandler
    # @return:
    #   updated instance of serviceorderhanlder with updated output params
    def delBuf(self, obj):
        # input params
        resourceId = obj.resourceId
        bufNo = obj.bufNo
        # delete buffer/ reset buffer
        plc = StatePLC.objects.all().filter(id=resourceId)
        if plc.count() == 1:
            plc = plc.first()
            buffer = Buffer.objects.filter(resourceId=plc.id)
            if bufNo == 1:
                self.logger.info(
                    "[DELBUF] Delete bufferOut of resource " + str(resourceId))
                buffer.update(bufOutONo=0)
                buffer.update(bufOutOPos=0)
            elif bufNo == 2:
                self.logger.info(
                    "[DELBUF] Delete bufferIn of resource " + str(resourceId))
                buffer.update(bufInONo=0)
                buffer.update(bufInOPos=0)

        # set output parameter
        obj.resourceId = 0
        obj.bufNo = 0
        return obj

    # get all parts signed as unknown, needed for robotinos/fleetmanager
    # @param:
    #   obj: instance of serviceorderhandler
    # @return:
    #   updated instance of serviceorderhanlder with updated output params
    def getUnknownParts(self, obj):
        # input params
        maxRecords = obj.maxRecords
        # undefined parts
        undefinedPart = ["undefined box", "undefined"]
        undefinedPNo = [21, 26]

        # write undefined parts into serviceParams
        serviceParams = []
        for i in range(len(undefinedPart)):
            serviceParams.append(undefinedPNo[i])
            part = undefinedPart[i]
            for j in range(len(part)):
                serviceParams.append(ord(part[j]))
            serviceParams.append(0)
            while len(serviceParams) < 35 * i:
                serviceParams.append(0)
        for i in range((35 * maxRecords) - len(serviceParams)):
            serviceParams.append(0)

        obj.serviceParams = serviceParams
        obj.pNo = undefinedPNo[0]
        obj.dataLength = 140
        return obj

    # get transportation tasks
    # @param:
    #   obj: instance of serviceorderhandler
    # @return:
    #   updated instance of serviceorderhanlder with updated output params
    def getToAGVBuf(self, obj):
        # input parameter
        maxRecords = obj.maxRecords
        # get ids of resource where the robotino gets the part and the id
        # to where the robotino delivers the part
        currentOrder = AssignedOrder.objects.all()
        serviceParams = []
        currentRecords = 0
        if currentOrder.count() != 0:
            for order in currentOrder:
                status = order.getStatus()
                startId = 0
                targetId = 0
                for i in range(len(status)):
                    # find first unfinished step => first unfinished
                    # step is target and the step before is start
                    if status[i] == 0:
                        if i > 0:
                            workingSteps = order.assigendWorkingPlan.workingSteps.all()
                            targetId = workingSteps[i].assignedToUnit
                            startId = workingSteps[i-1].assignedToUnit
                            break
                        else:
                            break

                # change startId/targetID to 2, if start/target is storage which hasnt a dock
                if startId == 1:
                    startId = 2
                if targetId == 1:
                    targetId = 2
                # change startId/targetId if they are resource 3/4, because there robotino docks at 4 every time
                if startId == 3:
                    startId = 4
                if targetId == 3:
                    targetId = 4

                # set params for servicespecific output parameter
                startBufNo = 1  # bufOut of branch
                startBufPos = 1  # always 1 for branch
                startBeltNo = 1  # always 1 for branch
                # get target position
                targetBufNo = 2  # bufIn of branch
                targetBufPos = 1    # always 1 for branch
                targetBeltNo = 1    # always 1 for branch
                answerParameterlist = [
                    startId,
                    startBufNo,
                    startBufPos,
                    startBeltNo,
                    targetId,
                    targetBufNo,
                    targetBufPos,
                    targetBeltNo
                ]
                # only do buffer check if MES uses Fleetmanager
                if Setting.objects.all().first().useFleetmanager:
                    # only set output parameter if bufferIn from target is empty and
                    # if bufferOut from start isnt empty
                    if Buffer.objects.filter(resourceId=startId).count != 0 and Buffer.objects.filter(resourceId=targetId).count() != 0:
                        bufOutStart = Buffer.objects.filter(
                            resourceId=startId).first()
                        bufInTarget = Buffer.objects.filter(
                            resourceId=targetId).first()
                        if bufInTarget.bufInONo == 0 and bufOutStart.bufOutONo != 0:
                            # only add transport task to output params if length of records doesnt
                            # exceed specified maxRecords from Fleetmanager
                            if currentRecords < maxRecords:
                                serviceParams.extend(answerParameterlist)
                                currentRecords += 1
                # just set transportation task without buffer check
                else:
                    if currentRecords < maxRecords:
                        serviceParams.extend(answerParameterlist)
                        currentRecords += 1
            # pad parameterlist to required length with 0
            for i in range(8 * maxRecords - len(serviceParams)):
                answerParameterlist.append(0)

            # set output parameter
            obj.maxRecords = 0
            if len(serviceParams) == 0:
                obj.dataLength = 0
                obj.serviceParams = []
            else:
                # datalength = maxRecords * 8 entries per record
                # and 2 byte per item in entry
                obj.dataLength = maxRecords * 8 * 2
                obj.serviceParams = serviceParams
                self.logger.info("[GETTOAGVBUF] Found start " + str(startId) +
                                 " and target " + str(targetId)+" for Robotinos")
        else:
            obj.dataLength = 0
            obj.serviceParams = []
        return obj

    # write the actuall AGV Position Aux1Int = AgvId
    # @param:
    #   obj: instance of serviceorderhandler
    # @return:
    #   updated instance of serviceorderhanlder with updated output params
    def setAgvPos(self, obj):
        # input parameter
        robotinoId = obj.aux1Int
        dockedAt = obj.resourceId

        # update resource id where robotino is docked
        robotino = StatePLC.objects.all().filter(id=robotinoId)
        if robotino.count() == 1:
            robotino.update(dockedAt=dockedAt)
            self.logger.info("[SETAGVPOS] Robotino with id " + str(robotinoId) +
                             " docked at resource " + str(dockedAt))
        # set output parameter
        obj.aux1Int = 0
        obj.resourceId = 0
        return obj

    # send Visualisation task to specified visualisation uniot
    # @param:
    #   orderNo: ordernumber of order where visualisationtask is assigned to
    #   orderPos: orderposition of order where visualisationtask is assigned to
    #   resourceId: Id of resource where visualisationunit should be mounted on
    #   stepNo: stepNo of workingstep which the visualisation task corresponds to
    def _sendVisualisationTask(self, orderNo, orderPos, resourceId, stepNo):
        from .safteymonitoring import SafteyMonitoring
        # get task
        order = AssignedOrder.objects.filter(
            orderNo=orderNo).filter(orderPos=orderPos).first()
        visualisationTasks = order.assigendWorkingPlan.workingSteps.filter(
            stepNo=stepNo).filter(assignedToUnit=resourceId)
        if(visualisationTasks.count() != 0):
            task = visualisationTasks.first()
            # send task
            payload = {
                "task": task.task,
                "assignedWorkingPiece": order.assignedWorkingPiece,
                "stepNo": stepNo,
                "paintColor": task.color
            }
            try:
                request = requests.put("http://" +
                                       StateVisualisationUnit.objects.filter(
                                           boundToRessource=resourceId).first().ipAdress
                                       + ':5000/api/VisualisationTask', data=payload)

                if not request.ok:
                    safteyMonitoring = SafteyMonitoring()
                    safteyMonitoring.decodeError(
                        errorLevel=safteyMonitoring.LEVEL_ERROR,
                        errorCategory=safteyMonitoring.CATEGORY_CONNECTION,
                        msg="Visualisation unit is not reachable. Check connection of the unit to the MES. Ordernumber and orderposition:" +
                        str(orderNo) + ":" + str(orderPos))

            except Exception as e:
                safteyMonitoring = SafteyMonitoring()
                safteyMonitoring.decodeError(
                    errorLevel=safteyMonitoring.LEVEL_ERROR,
                    errorCategory=safteyMonitoring.CATEGORY_CONNECTION,
                    msg=str(e)
                )
