"""
Filename: servicecalls.py
Version name: 0.1, 2021-05-18
Short description: Module for handling the service calls. The buisness logic for each servicecall
is handled here. Given on the servicecalls some output parameters are set

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

from os import stat
from mesapi.models import AssignedOrder, Buffer, Costumer, Setting, StatePLC, StateVisualisationUnit, WorkingPlan, WorkingStep, StateWorkingPiece
import logging


class Servicecalls(object):

    def __init__(self):
        from .systemmonitoring import SystemMonitoring
        self.systemmonitoring = SystemMonitoring()
        # setup logging
        logging.basicConfig(filename="orders.log",
                            level=logging.INFO, format='[%(asctime)s ] %(name)s : %(message)s')
        self.logger = logging.getLogger("servicecalls")
        self.logger.setLevel(logging.INFO)

    # get first unfinished operation for resource

    def getFirstOpForRsc(self, obj):
        resourceId = obj.resourceId
        self.logger.info(
            "[SERVICEORDERHANDLER] Request GetFirstOpForRsc for resource " + str(resourceId))
        print(
            "[SERVICEORDERHANDLER] Request GetFirstOpForRsc for resource " + str(resourceId))

        # Load current orders and  and determine if the ressource has a working step in it
        currentOrder = AssignedOrder.objects.all()
        for order in currentOrder:
            workingPlan = order.assigendWorkingPlan
            workingsteps = workingPlan.workingSteps.all().filter(assignedToUnit=resourceId)
            status = order.getStatus()
            stepPos = 0
            if workingsteps.count() != 0:
                step = workingsteps.first()
                stepsToCheck = workingPlan.workingSteps.all()
                # search position in workingsteps
                for i in range(len(status)):
                    if stepsToCheck[i].id == step.id:
                        stepPos = i
                # only start operation if it isnt already finished
                if status[stepPos] == 0:
                    self.logger.info(
                        "[GETFIRSTOPFORRSC] Found active order for resource " + str(resourceId))
                    print(
                        "[GETFIRSTOPFORRSC] Found active order for resource " + str(resourceId))
                    # set output parameter
                    obj.stepNo = step.stepNo
                    obj.oNo = order.orderNo
                    obj.oPos = order.orderPos
                    obj.wpNo = workingPlan.workingPlanNo
                    obj.opNo = step.operationNo
                    obj.stopperId = 0
                    if order.costumer != None:
                        obj.cNo = order.costumer.costumerNo
                    obj.mainOPos = order.mainOrderPos
                    obj.errorStepNo = 0
                    if step.operationNo == 210 or step.operationNo == 211:
                        # set output params
                        obj.dataLength = 12
                        bufPos = Setting.objects.all().first().getFirstFreePlace()
                        workingPiece = StateWorkingPiece.objects.filter(
                            id=currentOrder.assignedWorkingPiece.id)
                        partNo = workingPiece.first().partNo
                        if step.operationNo == 210:
                            # store from stopper 1
                            obj.stopperId = 1
                            # serviceparams[constant, position in storage, part number], each param has 2 bytes, so each param is padded with a 0
                            obj.serviceParams = [
                                0, 90, 0, bufPos, 0, partNo]
                        else:
                            # store from stopper 2
                            obj.stopperId = 2
                            obj.serviceParams = [
                                0, 91, 0, bufPos, 0, partNo]
                        # update mes data
                        workingPiece.update(storageLocation=obj.bufPos)
                        workingPiece.update(carrierId=0)
                        Setting.objects.all().first().updateStoragePosition(obj.bufPos, False)
                    # operation is manual work
                    elif step.operationNo == 510:
                        obj.stopperId = 0
                        obj.serviceParams = [0, 3, 0, 4,
                                             0, 25, 0, 0, 0, 0, 0, 0, 0, 0]
                        obj.dataLength = 28
                    # operation is delay
                    elif step.operationNo == 1110:
                        obj.stopperId = 0
                        delayTime = 5
                        obj.dataLength = 2
                        # serviceparam[seconds], seconds = seconds which the carrier will wait,
                        # param consists of two bytes, so param is padded with leading zero (big endian)
                        obj.serviceParams = [0, delayTime]
                else:
                    obj.resourceId = 0
                    obj.stopperId = 0
                    obj.serviceParams = [0, 0]
                    obj.dataLength = 4
                # update mes data
                workingPiece = order.assignedWorkingPiece
                workingPiece.location = resourceId
                workingPiece.save()
                return obj
            else:
                obj.resourceId = 0
                obj.serviceParams = [0, 0]
                obj.dataLength = 4

        return obj

    # get next operation for ONo and OPos
    def getOpForONoOPos(self, obj):
        requestId = obj.requestID
        stopperId = obj.stopperId
        oNo = obj.oNo
        oPos = obj.oPos
        # self.logger.info("[GETOPFORONOOPOS] " + str(oNo))
        # print("[GETOPFORONOOPOS]  "  + str(oNo))
        obj.stopperId = 0
        # Load current orders and search if theres a order according to orderNo and Opos
        currentOrder = AssignedOrder.objects.all().filter(
            orderNo=oNo).filter(orderPos=oPos)
        if currentOrder.count() == 1:
            currentOrder = currentOrder.first()
            workingPlan = currentOrder.assigendWorkingPlan
            workingsteps = workingPlan.workingSteps.all()
            status = currentOrder.getStatus()
            for i in range(len(status)):
                # find first step which isnt execurted yet
                if status[i] == 0:
                    # only send operation if step is assigned to requested unit
                    if workingsteps[i].assignedToUnit == requestId:
                        self.logger.info(
                            "[GETOPFORONOOPOS] Found active order for ordernumber " + str(oNo)+" for resource " + str(requestId))
                        print("[GETOPFORONOOPOS] Found active order for ordernumber " +
                              str(oNo)+" for resource " + str(requestId))
                        # set general output parameter
                        obj.stepNo = workingsteps[i].stepNo
                        obj.resourceId = workingsteps[i].assignedToUnit
                        obj.wpNo = workingPlan.workingPlanNo
                        obj.opNo = workingsteps[i].operationNo
                        if currentOrder.costumer != None:
                            #obj.cNo = currentOrder.costumer.costumerNo
                            obj.cNo = 0
                        else:
                            obj.cNo = 0
                        obj.mainOPos = currentOrder.mainOrderPos
                        obj.errorStepNo = 0
                        obj.pNo = 25  # 25= pallet, 31 = carrier
                        obj.carrierId = currentOrder.assignedWorkingPiece.carrierId
                        # set output params specific to operation
                        # operation is store a part
                        if workingsteps[i].operationNo == 210 or workingsteps[i].operationNo == 211:
                            # set output params
                            obj.dataLength = 12
                            bufPos = Setting.objects.all().first().getFirstFreePlace()
                            workingPiece = StateWorkingPiece.objects.filter(
                                id=currentOrder.assignedWorkingPiece.id)
                            partNo = workingPiece.first().partNo
                            if workingsteps[i].operationNo == 210:
                                # store from stopper 1
                                obj.stopperId = 1
                                # serviceparams[constant, position in storage, part number], each param has 2 bytes, so each param is padded with a 0
                                obj.serviceParams = [
                                    0, 90, 0, bufPos, 0, partNo]
                            else:
                                # store from stopper 2
                                obj.stopperId = 2
                                obj.serviceParams = [
                                    0, 91, 0, bufPos, 0, partNo]
                            # update mes data
                            workingPiece.update(storageLocation=obj.bufPos)
                            workingPiece.update(carrierId=0)
                            Setting.objects.all().first().updateStoragePosition(obj.bufPos, False)
                        # operation is manual work
                        elif workingsteps[i].operationNo == 510:
                            obj.serviceParams = [0, 3, 0, 4,
                                                 0, 25, 0, 0, 0, 0, 0, 0, 0, 0]
                            obj.dataLength = 28
                        # operation is delay
                        elif workingsteps[i].operationNo == 1110:
                            delayTime = 5
                            obj.dataLength = 2
                            # serviceparam[seconds], seconds = seconds which the carrier will wait,
                            # param consists of two bytes, so param is padded with leading zero (big endian)
                            obj.serviceParams = [0, delayTime]
                    else:
                        obj.oNo = 0
                        obj.oPos = 0
                        obj.stopperId = 0
        return obj

    # get operation that is for this Stopper and the PNo is available
    def getOpForASRS(self, obj):
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
                    # check if step is for ASRS
                    if workingsteps[i].assignedToUnit == resourceId and not(workingsteps[i].operationNo == 210 or  workingsteps[i].operationNo ==211) :
                        self.logger.info(
                            "[GETOPFORASRS] Found active order for ASRS")
                        print("[GETOPFORASRS] Found active order for ASRS")
                        # set general output parameter
                        obj.oNo = order.orderNo
                        obj.oPos = order.orderPos
                        obj.stepNo = workingsteps[i].stepNo
                        obj.resourceId = workingsteps[i].assignedToUnit
                        obj.wpNo = workingPlan.workingPlanNo
                        obj.opNo = workingsteps[i].operationNo
                        obj.bufNo = 1
                        if order.costumer != None:
                            #obj.cNo = order.costumer.costumerNo
                            obj.Cno = 0
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
                        # set output parameter depending on stopper from which request is send
                        if obj.opNo == 212  or obj.opNo == 213:
                            if obj.opNo == 212:
                                obj.stopperId = 1
                                # serviceparams[constant, position in storage, part number], each param has 2 bytes, so each param is padded with a 0
                                obj.serviceParams = [
                                    0, 90, 0, obj.bufPos, 0, partNo]
                            elif obj.opNo == 213:
                                
                                obj.stopperId = 2
                                obj.serviceParams = [
                                    0, obj.bufPos, 0, 91 , 0, partNo]
                                self.logger.info(str(obj.serviceParams))
                                print(obj.serviceParams)
                            # update mes data
                            setting = Setting.objects.all().first()
                            setting.updateStoragePosition(
                               workingPiece.storageLocation, True)
                            setting.save()
                            #workingPiece.storageLocation = 0
                            #order.assignedWorkingPiece.save()
                            return obj
                    else:
                        obj.stopperId = 0
                        obj.serviceParams = [0, 0]
                        obj.dataLength = 4
                        return obj
                else:
                    # no active order for asrs
                    obj.stopperId = 0
        return obj

    # get the free string for the actual order field defined as parameter will be replaced
    def getFreeString(self, obj):
        requestId = obj.requestID
        oNo = obj.oNo
        oPos = obj.oPos
        order = AssignedOrder.objects.all().filter(
            orderNo=oNo).filter(orderPos=oPos)
        freeString = ""
        if order.count() == 1:
            order = order.first()
            step = order.assigendWorkingPlan.workingSteps.filter(
                assignedToUnit=requestId).first()
            obj.stepNo = str(step.stepNo)
            obj.stepNo = step.stepNo
        # parse freestring
            freeString = "http://" + Setting.objects.all().first().ipAdressMES4 + "/I4.0/mes4/EN/mes4.php?content=manual&OpNo=" + \
                str(step.stepNo) + "&Workpiece=3"+"&Action=4" + "&PNo=25"
        serviceParams = []
        # max length of string
        serviceParams.append(254)
        # actual length of string
        serviceParams.append(len(freeString))
        for i in range(2, serviceParams[1]):
            serviceParams.append(ord(freeString[i]))

        while len(serviceParams) != serviceParams[0]+2:
            serviceParams.append(0)

        obj.serviceParams = serviceParams
        obj.dataLength = 256
        return obj

    # set parameters on runtime
    def setPar(self, obj):
        requestId = obj.requestID
        oNo = obj.oNo
        oPos = obj.oPos
        # Load current orders and search if theres a order according to orderNo and Opos
        currentOrder = AssignedOrder.objects.all()
        for order in currentOrder:
            if order.orderNo == oNo and order.orderPos == oPos:
                self.logger.info("[SETPAR] Found order to set parameter")
                print("[SETPAR] Found order to set parameter")
                break
        obj.stepNo = 0
        obj.resourceId = 0
        obj.wpNo = 0
        obj.opNo = 0
        obj.cNo = 0
        obj.mainOPos = 0
        obj.errorStepNo = 0
        obj.pNo = 0
        obj.carrierId = 0
        obj.serviceParams = []
        return obj

    # operation start
    def opStart(self, obj):
        requestId = obj.requestID
        oNo = obj.oNo
        oPos = obj.oPos
        # Load current orders and search if theres a order according to orderNo and Opos
        currentOrder = AssignedOrder.objects.all().filter(
            orderNo=oNo).filter(orderPos=oPos)
        if currentOrder.count() == 1:
            # TODO send state of workingpiece to visualisation unit
            self.logger.info(
                "[OPSTART] Operation  started on resource " + str(requestId))
            print("[OPSTART] Operation started on resource " + str(requestId))
            # set output parameter
            obj.stepNo = 0
            obj.resourceId = 0
            obj.wpNo = 0
            obj.opNo = 0
            obj.cNo = 0
            obj.mainOPos = 0
            obj.errorStepNo = 0
            obj.pNo = 0
            obj.carrierId = 0
            # update mes data
            workingpiece = currentOrder.first().assignedWorkingPiece
            workingpiece.location = requestId
            workingpiece.save()
        return obj

    # reset start operation
    def opReset(self, obj):
        # input parameter
        oNo = obj.oNo
        oPos = obj.oPos
        requestId = obj.requestID
        # order = AssignedOrder.objects.filter(
        #     orderNo=oNo).filter(orderPos=oPos).first()
        # workingsteps = order.assigendWorkingPlan.workingSteps.all().filter(
        #     assignedToUnit=requestId)
        # status = order.getStatus()
        # for i in range(len(status)):
        #     if workingsteps[i].assignedToUnit == requestId:
        #         # update status of task to unfinished if it is marked as finished
        #         if status[i] == 1:
        #             status[i] = 0
        #             order.setStatus(status)
        #             order.save()
        #             self.logger.info(
        #                 "[OPRESET] Reset operation  on resource " + str(requestId))
        #             print("[OPSTART] Reset operation on resource " +
        #                   str(requestId))

        # set output parameter
        obj.oNo = 0
        obj.oPos = 0
        return obj

    # operation end. Sends next operation to resource to write on NFC tag
    def opEnd(self, obj):
        # get input parameter
        requestId = obj.requestID
        oNo = obj.oNo
        oPos = obj.oPos
        carrierId = obj.carrierId

        # Find corresponding order
        currentOrder = AssignedOrder.objects.all().filter(
            orderNo=oNo).filter(orderPos=oPos)
        stateVisualisationUnit = StateVisualisationUnit.objects.all().filter(
            boundToRessource=requestId)
        if currentOrder.count() != 0:
            order = currentOrder.first()
            workingPlan = order.assigendWorkingPlan
            workingsteps = workingPlan.workingSteps.all()
            status = order.getStatus()
            for i in range(len(status)):
                # find first unfinished step in list
                if status[i] == 0:
                    # set output parameters
                    # Write NFC tags, data for NFC tag can be manipulated
                    self.logger.info("[OPEND] Operation " + str(obj.opNo) + " on resource " +
                                     str(requestId) + " ended. Writing next operation on RFID")
                    print("[OPEND] Operation " + str(obj.opNo) + " on resource " +
                          str(requestId) + " ended. Writing next operation on RFID")
                    # If visualisationunit finished task then write next step of workingplan on rfid,
                    # only check if resource is branch
                    if stateVisualisationUnit.count() != 0:
                        stateVisualisationUnit = stateVisualisationUnit.first()
                        if stateVisualisationUnit.state == "finished" or stateVisualisationUnit.state == "idle" and requestId > 1 and requestId < 7:
                            if i+1 < len(status):
                                obj.stepNo = workingsteps[i+1].stepNo
                                obj.resourceId = workingsteps[i +
                                                              1].assignedToUnit
                                obj.opNo = workingsteps[i+1].operationNo
                        # If visualisationunit hasnt finished, then write current task again to repeat operation on PLC,
                        # only check if resource is branch
                        elif stateVisualisationUnit.state == "playing" or stateVisualisationUnit.state == "waiting" and requestId > 1 and requestId < 7:
                            self.logger.info(
                                "[OPEND] Attached visualisationunit hasnt finished. Write same step again on RFID to repeat operation")
                            print(
                                "[OPEND] Attached visualisationunit hasnt finished. Write same step again on RFID to repeat operation")
                            obj.stepNo = workingsteps[i].stepNo
                            obj.resourceId = workingsteps[i].assignedToUnit
                            obj.opNo = workingsteps[i].operationNo
                    else:
                        if i+1 < len(status):
                            obj.stepNo = workingsteps[i+1].stepNo
                            obj.resourceId = workingsteps[i+1].assignedToUnit
                            obj.opNo = workingsteps[i+1].operationNo
                    obj.oNo = order.orderNo
                    obj.oPos = order.orderPos
                    obj.stepNo = 0
                    obj.wpNo = workingPlan.workingPlanNo
                    obj.cNo = order.costumer.costumerNo
                    obj.mainOPos = order.mainOrderPos
                    obj.errorStepNo = 0
                    obj.pNo = 25  # 25= pallet, 31 = carrier

                    # update data
                    workingpiece = StateWorkingPiece.objects.filter(
                        id=order.assignedWorkingPiece.id)
                    workingpiece.update(carrierId=carrierId)
                    workingpiece.update(location=requestId)
                    status[i] = 1
                    order.setStatus(status)
                    order.save()
                    # all steps in workingplan are complete => delete order
                    if not 0 in status:
                        order.delete()
                    break
        else:
            obj.oNo = 0
            obj.oPos = 0
            obj.carrierId = 0
        return obj

    # get shunt for target resource
    def getShuntForTarget(self, obj):
        requestID = obj.requestID
        currentOrder = AssignedOrder.objects.all()
        for order in currentOrder:
            workingPlan = order.assigendWorkingPlan
            workingsteps = workingPlan.workingSteps.all()
            status = order.getStatus()
            for i in range(len(status)):
                if status[i] == 0:
                    obj.dataLength = 2
                    # serviceparams[position] with position = 1 straight forward and position=2 to bufOut
                    # workingpiece is on brqanch 2 and has to go to storage
                    if workingsteps[i].assignedToUnit == 1 and requestID == 2:
                        self.logger.info("[GETSHUNTFORTARGET] Branch for resource " +
                                         str(requestID) + " is set to straight forward")
                        print("[GETSHUNTFORTARGET] Branch for resource " +
                              str(requestID) + " is set to straight forward")

                        obj.serviceParams = [1]
                        break
                    # workingpiece is on branch 3 or 4 which are connected and has to stay on the two of them
                    elif (workingsteps[i].assignedToUnit == 3 and requestID == 4) or (workingsteps[i].assignedToUnit == 4 and requestID == 3):
                        self.logger.info("[GETSHUNTFORTARGET] Branch for resource " +
                                         str(requestID) + " is set to straight forward")
                        print("[GETSHUNTFORTARGET] Branch for resource " +
                              str(requestID) + " is set to straight forward")
                        obj.serviceParams = [1]
                        break
                    # workingpiece has to leave resource
                    elif workingsteps[i].assignedToUnit != requestID:
                        self.logger.info("[GETSHUNTFORTARGET] Branch for resource " +
                                         str(requestID) + " is set to buffer out")
                        print("[GETSHUNTFORTARGET] Branch for resource " +
                              str(requestID) + " is set to buffer out")
                        obj.serviceParams = [2]
                        break
                    # workingpiece has to stay on the resource
                    else:
                        self.logger.info("[GETSHUNTFORTARGET] Branch for resource " +
                                         str(requestID) + " is set to straight forward")
                        print("[GETSHUNTFORTARGET] Branch for resource " +
                              str(requestID) + " is set to straight forward")
                        obj.serviceParams = [1]
                        break
        return obj

    # get all BufPos for defined BufNo and resource
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
                if plcBuf.bufferOut:
                    bufPos = 1
                    oNo = plcBuf.bufOutONo
                    oPos = plcBuf.bufOutOPos
                    pNo = 25
                else:
                    obj.pNo = 0
            elif bufNo == 2:
                if plcBuf.bufferIn:
                    bufPos = 1
                    oNo = plcBuf.bufOutONo
                    oPos = plcBuf.bufOutOPos
                    pNo = 25
                    pNo = 25

        self.logger.info(
            "[GETBUFFORBUFNO] Returned buffer to resource " + str(resourceId))
        print("[GETBUFFORBUFNO] Returned buffer to resource " + str(resourceId))
        serviceParams = [bufPos, oPos, oNo, pNo, 0]
        obj.serviceParams = serviceParams
        return obj

    # get buffer of defined BufPos
    def getBufPos(self, obj):
        # get input parameter
        resourceId = obj.resourceId
        bufNo = obj.bufNo
        bufPos = obj. bufPos

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
                    setting = Setting.objects.all().first()
                    storage = setting.getStatus()
                    if storage[bufPos] == 1:
                        obj.pNo = 25
                        obj.boxPNo = 25
                    else:
                        obj.pNo = 0
                        obj.boxPNo = 0
            # PLC is robotino or branch
            elif resourceId != 1:
                if bufNo == 1 and bufPos == 1:
                    if plcBuf.bufferOut:
                        obj.pNo = 25
                        obj.boxPNo = 25
                        obj.oNo = plcBuf.bufOutONo
                        obj.oPos = plcBuf.bufOutOPos
                    else:
                        obj.pNo = 0
                        obj.oNo = 0
                        obj.oPos = 0
                elif bufNo == 2 and bufPos == 1:
                    if plcBuf.bufferIn:
                        obj.pNo = 25
                        obj.boxPNo = 25
                        obj.oNo = plcBuf.bufInONo
                        obj.oPos = plcBuf.bufOutOPos
                    else:
                        obj.pNo = 0
                        obj.oNo = 0
                        obj.oPos = 0
        else:
            obj.pNo = 0
            obj.oNo = 0
            obj.oPos = 0
            obj.palletID = 0
            obj.boxId = 0
        self.logger.info(
            "[GETBUFPOS] Returned buffer of resource " + str(resourceId))
        print("[GETBUFPOS] Returned buffer of resource " + str(resourceId))
        return obj

    # get buffer from the docked AGV
    def getBufDockedAgv(self, obj):
        requestId = obj.requestID
        plcs = StatePLC.objects.all()
        for resource in plcs:
            if resource.id>=7:
                plc= resource
                buffer = plc.buffer
                if buffer.bufferOut:
                    break
        # bufNo and bufPos are always 1 on robotino
        self.logger.info("RessourceId: " + str(obj.resourceId))
        obj.bufNo = 1
        obj.bufPos = 1
        # check if a workingpiece is on the robotino
        obj.oNo = buffer.bufOutONo
        obj.oPos = buffer.bufOutOPos
        #obj.pNo = stateWorkingPiece.partNo
        obj.pNo = 25
        self.logger.info(
            "[GETBUFDOCKEDAGV] Returned buffer of docked robotino " + str(obj.resourceId) + " to resource " + str(requestId))
        print(
            "[GETBUFDOCKEDAGV] Returned buffer of docked robotino " + str(obj.resourceId) + " to resource " + str(requestId))

        return obj

    # move a buffer from source to target (for buffer and FIFO)
    def moveBuf(self, obj):
        self.logger.info("[SERVICEORDERHANDLER] Request MoveBuf")
        print("[SERVICEORDERHANDLER] Request MoveBuf")
        # input parameter
        inputParameter = obj.serviceParams

        # get buffer from request which should be moved
        oldId = inputParameter[0]
        oldBufNo = inputParameter[1]
        #oldBufPos = inputParameter[2]
        newId = inputParameter[3]
        newBufNo = inputParameter[4]
        #newBufPos = inputParameter[5]

        # update buffer
        originPlc = StatePLC.objects.all().filter(id=oldId)
        targetPlc = StatePLC.objects.all().filter(id=newId)
        if originPlc.count() == 1 and targetPlc.count() == 1:
            # get buffer
            oldbuffer = Buffer.objects.filter(resourceId=oldId)
            targetbuffer = Buffer.objects.filter(resourceId=newId)
            if newBufNo == 1:
                targetbuffer.update(bufferOut=True)
                targetbuffer.update(bufOutONo=oldbuffer.first().bufOutONo)
                targetbuffer.update(bufOutOPos=oldbuffer.first().bufOutOPos)
            elif newBufNo == 2:
                targetbuffer.update(bufferIn=True)
                targetbuffer.update(bufInONo=oldbuffer.first().bufInONo)
                targetbuffer.update(bufInOPos=oldbuffer.first().bufInOPos)
        # update origin buffer
            # update source buffer (only if old buffer isnt robotino)
            if oldId < 7:
                if oldBufNo == 1:
                    oldbuffer.update(bufferOut=False)
                    oldbuffer.update(bufOutONo=0)
                    oldbuffer.update(bufOutOPos=0)
                elif oldBufNo == 2:
                    oldbuffer.update(bufferIn=False)
                    oldbuffer.update(bufInONo=0)
                    oldbuffer.update(bufInOPos=0)
        self.logger.info("[MOVEBUF] Moved buffer from resource " +
                         str(oldId) + " to resource " + str(newId))
        print("[MOVEBUF] Moved buffer from resource " +
              str(oldId) + " to resource " + str(newId))

        # update location of workingpiece
        StateWorkingPiece.objects.filter(location=oldId).update(location=newId)
        # set output parameter
        obj.serviceParams = []
        obj.dataLength = 0
        return obj

    # write in buffer; Aux1Int = Quantity of a stack buffer
    def setBufPos(self, obj):
        requestId = obj.requestID
        resourceId = obj.resourceId
        self.logger.info("[SERVICEORDERHANDLER] Request SetBufPos for resource " + str(resourceId))
        print("[SERVICEORDERHANDLER] Request SetBufPos for resource " + str(resourceId))
        # get input parameter
    
        bufNo = obj.bufNo
        bufPos = obj.bufPos
        partNo = obj.pNo
        oNo = obj.oNo
        oPos = obj.oPos

        # update buffer of plc
        statePlc = StatePLC.objects.all().filter(id=obj.resourceId)
        if statePlc.count() == 1:
            # PLC isnt storage
            if resourceId != 1:
                statePlc = statePlc.first()
                buffer = Buffer.objects.filter(resourceId=statePlc.id)
                if bufNo == 1:
                    if oNo != 0:
                        buffer.update(bufferOut=True)
                        buffer.update(bufOutONo=oNo)
                        buffer.update(bufOutOPos=oPos)
                    elif oNo == 0:
                        buffer.update(bufferOut=False)
                        buffer.update(bufOutONo=0)
                        buffer.update(bufOutOPos=0)
                elif bufNo == 2:
                    if oNo != 0:
                        buffer.update(bufferIn=True)
                        buffer.update(bufInONo=oNo)
                        buffer.update(bufInOPos=oPos)
                    elif oNo == 0:
                        buffer.update(bufferIn=False)
                        buffer.update(bufInONo=0)
                        buffer.update(bufInOPos=0)
            # PLC is storage
            elif resourceId == 1:
                if bufNo == 1:
                    if partNo != 0:
                        setting = Setting.objects.all().first()
                        setting.updateStoragePosition(bufPos, False)
                        setting.save()
                    elif partNo == 0:
                        setting = Setting.objects.all().first()
                        setting.updateStoragePosition(bufPos, True)
                        setting.save()

        # system return all parameter as 0
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
        print("[SETBUFPOS] Buffer for resource " + str(resourceId) + " set")
        return obj

    # delete all positions of a defined buffer
    def delBuf(self, obj):
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
                print("[DELBUF] Delete bufferOut of resource " + str(resourceId))
                buffer.update(bufferOut=False)
                buffer.update(bufOutONo=0)
                buffer.update(bufOutOPos=0)
            elif bufNo == 2:
                self.logger.info(
                    "[DELBUF] Delete bufferIn of resource " + str(resourceId))
                print("[DELBUF] Delete bufferIn of resource " + str(resourceId))
                buffer.update(bufferIn=False)
                buffer.update(bufInONo=0)
                buffer.update(bufInOPos=0)

        # set output parameter
        obj.resourceId = 0
        obj.bufNo = 0
        return obj

    # get all parts signed as unknown
    def getUnknownParts(self, obj):
        maxRecords = obj.maxRecords

        undefinedPart = ["undefined box", "undefined"]
        undefinedPNo = [21, 26]

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

    # get a buffer where a AGV can get a defined Part
    def getToAGVBuf(self, obj):
        maxRecords = obj.maxRecords

        # get ids of resource where the robotino gets the part and the id
        # to where the robotino delivewrs the part
        currentOrder = AssignedOrder.objects.all()
        if currentOrder.count() != 0:
            currentOrder = currentOrder.first()
            status = currentOrder.getStatus()
            startId = 0
            targetId = 0
            for i in range(len(status)):
                # find first unfinished step. first unfinished
                # step is target and the step before is start
                if status[i] == 0:
                    workingSteps = currentOrder.assigendWorkingPlan.workingSteps.all()
                    # is final step which is to store a part in storage (where it has to deliver to resource 2)
                    if i == len(status)-1:
                        targetId = 2
                        startId = workingSteps[i-1].assignedToUnit
                    elif i >= 2:
                        targetId = workingSteps[i].assignedToUnit
                        startId = workingSteps[i-1].assignedToUnit
                    else:
                        targetId = workingSteps[i].assignedToUnit
                        startId = 0
                    self.logger.info("[GETTOAGVBUF] Found start " + str(startId) +
                                     " and target " + str(targetId)+" for Robotinos")
                    print("[GETTOAGVBUF] Found start " + str(startId) +
                          " and target " + str(targetId)+" for Robotinos")
                    break
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
            # pad parameterlist to required length with 0
            for i in range(160-len(answerParameterlist)):
                answerParameterlist.append(0)

        # set output parameter
        obj.maxRecords = 0
        obj.dataLength = 320
        obj.serviceParams = answerParameterlist
        return obj

    # write the actuall AGV Position Aux1Int = AgvId
    def setAgvPos(self, obj):
        # input parameter
        robotinoId = obj.aux1Int
        dockedAt = obj.resourceId

        # update resource id where robotino is docked
        robotino = StatePLC.objects.all().filter(id=robotinoId)
        if robotino.count() == 1:
            if dockedAt!=0:
                robotino.update(dockedAt=dockedAt)
                self.logger.info("[SETAGVPOS] Robotino with id " + str(robotinoId) +
                                " docked at resource " + str(dockedAt))
                print("[SETAGVPOS] Robotino with id " + str(robotinoId) +
                    " docked at resource " + str(dockedAt))
        # set output parameter
        obj.aux1Int = 0
        obj.resourceId = 0
        return obj
