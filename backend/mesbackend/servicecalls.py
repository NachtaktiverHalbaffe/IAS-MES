"""
Filename: servicecalls.py
Version name: 0.1, 2021-05-18
Short description: Module for handling the service calls. The buisness logic for each servicecall
is handled here. Given on the servicecalls some output parameters are set

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

from mesapi.models import AssignedOrder, Buffer, Costumer, Setting, StatePLC, StateVisualisationUnit, WorkingPlan, WorkingStep, StateWorkingPiece


class Servicecalls(object):

    def __init__(self):
        from .systemmonitoring import SystemMonitoring
        self.systemmonitoring = SystemMonitoring()

    # get first operation for resource
    def getFirstOpForRsc(self, obj):
        print("[SERVICEORDERHANDLER] Request GetFirstOpForRsc")
        resourceId = obj.resourceId
        # Load current orders and determine if the ressource has a working step in it
        currentOrder = AssignedOrder.objects.all()
        hasFoundOrder = False
        for order in currentOrder:
            workingPlan = order.assigendWorkingPlan
            workingsteps = workingPlan.workingSteps.all()
            for step in workingsteps:
                if step.assignedToUnit == resourceId:
                    print(
                        "[GETFIRSTOPFORRSC] Found active order for resource " + str(resourceId))
                    obj.stepNo = step.stepNo
                    obj.oNo = order.orderNo
                    obj.oPos = order.orderPos
                    obj.wpNo = workingPlan.workingPlanNo
                    obj.opNo = step.operationNo
                    obj.cNo = order.costumer.costumerNo
                    obj.mainOPos = order.mainOrderPos
                    obj.errorStepNo = 0
                    obj.pNo = 25  # 25= pallet, 31 = carrier
                    obj.serviceParams = [0, 0]
                    obj.dataLength = 4
                    hasFoundOrder = True
                    break
            if hasFoundOrder:
                # has found order, only first order is requested => exit
                break
        if not hasFoundOrder:
            print("[GETFIRSTOPFORRSC] No active order for resource " +
                  str(resourceId) + " found")
        return obj

    # get next operation for ONo and OPos
    def getOpForONoOPos(self, obj):
        print("[SERVICEORDERHANDLER] Request GetOpForONoOPos")
        requestId = obj.requestID
        oNo = obj.oNo
        oPos = obj.oPos
        obj.oNo = 0
        obj.oPos = 0
        # Load current orders and search if theres a order according to orderNo and Opos
        currentOrder = AssignedOrder.objects.all().filter(
            orderNo=oNo).filter(orderPos=oPos)
        if currentOrder.count() == 1:
            workingPlan = currentOrder.assigendWorkingPlan
            workingsteps = workingPlan.workingSteps.all()
            status = currentOrder.status
            for i in range(len(status)):
                # find first step which isnt execurted yet
                if status[i] == 0:
                    # only send operation if step is assigned to requested unit
                    if workingsteps[i].assignedToUnit == requestId:
                        print(
                            "[GETOPFORONOOPOS] Found active order for ordernumber " + str(oNo)+" for resource " + str(requestId))
                        obj.stepNo = workingsteps[i].stepNo
                        obj.resourceId = workingsteps[i].assignedToUnit
                        obj.wpNo = workingPlan.workingPlanNo
                        obj.opNo = workingsteps[i].operationNo
                        # if task is store a part
                        if workingsteps[i].operationNo == 210:
                            obj.stopperId = 1
                            obj.serviceParams = [0, 90, 0, 1, 0, 25]
                            obj.dataLength = 12
                            obj.bufPos = Setting.objects.all().first().getFirstFreePlace()
                        elif workingsteps[i].operationNo == 211:
                            obj.stopperId = 2
                            obj.serviceParams = [0, 1, 0, 90, 0, 25]
                            obj.dataLength = 12
                            obj.bufPos = Setting.objects.all().first().getFirstFreePlace()
                        else:
                            obj.stopperId = 0
                            obj.serviceParams = [0, 3, 0, 4,
                                                 0, 25, 0, 0, 0, 0, 0, 0, 0, 0]
                            obj.dataLength = 28
                        obj.cNo = currentOrder.costumer
                        obj.mainOPos = currentOrder.mainOrderPos
                        obj.errorStepNo = 0
                        obj.pNo = 25  # 25= pallet, 31 = carrier
                        obj.carrierId = currentOrder.assignedWorkingPiece.carrierId
                        break
                    else:
                        print(
                            "[GETOPFORONOOPOS] No active order for ordernumber " + str(oNo) + " for resource " + str(requestId) + " found")
                        obj.oNo = 0
                        obj.oPos = 0
                        obj.stopperId = 0
        return obj

    # get operation that is for this Stopper and the PNo is available
    def getOpForASRS(self, obj):
        print("[SERVICEORDERHANDLER] Request GetOpForASRS")
        resourceId = obj.resourceId
        stopperId = obj.stopperId
        currentOrder = AssignedOrder.objects.all()
        for order in currentOrder:
            workingPlan = order.assigendWorkingPlan
            workingsteps = workingPlan.workingSteps.all()
            status = order.status
            for i in range(len(status)):
                if status[i] == 0:
                    if workingsteps[i].assignedToUnit == resourceId:
                        print("[GETOPFORASRS] Found active order for ASRS")
                        obj.oNo = order.orderNo
                        obj.oPos = order.orderPos
                        obj.stepNo = workingsteps[i].stepNo
                        obj.resourceId = workingsteps[i].assignedToUnit
                        obj.wpNo = workingPlan.workingPlanNo
                        obj.opNo = workingsteps[i].operationNo
                        if obj.opNo == 212:
                            obj.stopperId = 1
                            obj.serviceParams = [0, 91, 0, 1, 0, 25]
                            obj.bufPos = order.assignedWorkingPiece.storageLocation
                        elif obj.opNo == 213:
                            obj.stopperId = 2
                            obj.serviceParams = [0, 1, 0, 91, 0, 25]
                            obj.bufPos = order.assignedWorkingPiece.storageLocation
                        obj.cNo = order.costumer
                        obj.mainOPos = order.mainOrderPos
                        obj.errorStepNo = 0
                        obj.pNo = 25  # 25= pallet, 31 = carrier
                        obj.carrierId = order.assignedWorkingPiece.carrierId
                        obj.bufNo = 1
                        obj.dataLength = 12
                        break
                    else:
                        print("[GETOPFORASRS] No active order for ASRS found")
                        obj.stopperId = 0
                        obj.serviceParams = [0, 0]
                        obj.dataLength = 4
                else:
                    print("[GETOPFORASRS] No active order for ASRS found")
                    obj.stopperId = 0

        return obj

    # get the free string for the actual order field defined as parameter will be replaced
    def getFreeString(self, obj):
        print("[SERVICEORDERHANDLER] Request GetFreeString")
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
        print("[SERVICEORDERHANDLER] Request SetPar")
        requestId = obj.requestID
        oNo = obj.oNo
        oPos = obj.oPos
        # Load current orders and search if theres a order according to orderNo and Opos
        currentOrder = AssignedOrder.objects.all()
        for order in currentOrder:
            if order.orderNo == oNo and order.orderPos == oPos:
                print("[SETPAR] Found order to set parameter")
                obj.stepNo = 0
                obj.resourceId = 0
                obj.wpNo = 0
                obj.opNo = 0
                obj.cNo = 0
                obj.mainOPos = 0
                obj.errorStepNo = 0
                obj.pNo = 0
                obj.carrierId = 0
                break
        return obj

    # operation start
    def opStart(self, obj):
        print("[SERVICEORDERHANDLER] Request OpStart")
        # to state update stuff
        requestId = obj.requestID
        oNo = obj.oNo
        oPos = obj.oPos
        # Load current orders and search if theres a order according to orderNo and Opos
        currentOrder = AssignedOrder.objects.all().filter(
            orderNo=oNo).filter(orderPos=oPos)
        if currentOrder.count() == 1:
            # TODO send state of workingpiece to
            print("[OPSTART] Operation " + str(obj.opNo) +
                  " started on resource " + str(requestId))
            obj.stepNo = 0
            obj.resourceId = 0
            obj.wpNo = 0
            obj.opNo = 0
            obj.cNo = 0
            obj.mainOPos = 0
            obj.errorStepNo = 0
            obj.pNo = 0
            obj.carrierId = 0
        return obj

    # reset start operation
    def opReset(self, obj):
        print("[SERVICEORDERHANDLER] Request OpReset")
        return

    # operation end. Sends next operation to resource to write on NFC tag
    def opEnd(self, obj):
        print("[SERVICEORDERHANDLER] Request OpEnd")
        requestId = obj.requestID
        oNo = obj.oNo
        oPos = obj.oPos
        carrierId = obj.carrierId
        currentOrder = AssignedOrder.objects.all()
        stateVisualisationUnit = StateVisualisationUnit.objects.all().filter(
            boundToRessource=requestId)
        hasFoundOrder = False
        for order in currentOrder:
            if oNo == order.orderNo and oPos == order.orderPos:
                workingPlan = order.assigendWorkingPlan
                workingsteps = workingPlan.workingSteps.all()
                status = order.status
                for i in range(len(status)):
                    if status[i] == 0:
                        # Write NFC tags, data for NFC tag can be manipulated
                        print("[OPEND] Operation " + str(obj.opNo) + " on resource " +
                              str(requestId) + " ended. Writing next operation on RFID")
                        # If visualisationunit finished task then write next step of workingplan on rfid, only check if resource is branch
                        if stateVisualisationUnit.count() != 0:
                            stateVisualisationUnit = stateVisualisationUnit.first()
                            if stateVisualisationUnit.state == "finished" or stateVisualisationUnit.state == "idle" and requestId > 1 and requestId < 7:
                                obj.stepNo = workingsteps[i+1].stepNo
                                obj.resourceId = workingsteps[i +
                                                              1].assignedToUnit
                                obj.opNo = workingsteps[i+1].operationNo
                            # If visualisationunit hasnt finished, then write current task again to repeat operation on PLC , only check if resource is branch
                            elif stateVisualisationUnit.state == "playing" or stateVisualisationUnit.state == "waiting" and requestId > 1 and requestId < 7:
                                print(
                                    "[OPEND] Attached visualisationunit hasnt finished. Write same step again on RFID to repeat operation")
                                obj.stepNo = workingsteps[i].stepNo
                                obj.resourceId = workingsteps[i].assignedToUnit
                                obj.opNo = workingsteps[i].operationNo
                        else:
                            obj.stepNo = workingsteps[i+1].stepNo
                            obj.resourceId = workingsteps[i+1].assignedToUnit
                            obj.opNo = workingsteps[i+1].operationNo
                        obj.oNo = order.orderNo
                        obj.oPos = order.orderPos
                        obj.stepNo = 0
                        obj.wpNo = workingPlan.workingPlanNo
                        obj.cNo = order.costumer
                        obj.mainOPos = order.mainOrderPos
                        obj.errorStepNo = 0
                        obj.pNo = 25  # 25= pallet, 31 = carrier
                        order.update(carrierId=carrierId)
                        status[i] = 1
                        order.setStatus(status)
                        hasFoundOrder = True
                        # all steps in workingplan are complete => delete order
                        if not 0 in status:
                            order.delete()
                        break
            if hasFoundOrder:
                break
        return obj

    # get shunt for target resource
    def getShuntForTarget(self, obj):
        print("[SERVICEORDERHANDLER] Request GetShuntForTarget")
        requestID = obj.requestID
        currentOrder = AssignedOrder.objects.all()
        for order in currentOrder:
            workingPlan = order.assigendWorkingPlan
            workingsteps = workingPlan.workingSteps.all()
            status = order.status
            for i in range(len(status)):
                if status[i] == 0:
                    if workingsteps[i].assignedToUnit != requestID:
                        print("[GETSHUNTFORTARGET] Branch for resource " +
                              str(requestID) + " is set to buffer out")
                        obj.serviceParam = [2]
                        break
                    else:
                        print("[GETSHUNTFORTARGET] Branch for resource " +
                              str(requestID) + " is set to straight forward")
                        obj.serviceParam = [1]
                        break
                obj.dataLength = 2
        return obj

    # get all BufPos for defined BufNo and resource
    def getBufForBufNo(self, obj):
        print("[SERVICEORDERHANDLER] Request GetBufForBufNo")
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

        print("[GETBUFFORBUFNO] Returned buffer to resource " + str(resourceId))
        serviceParams = [bufPos, oPos, oNo, pNo, 0]
        obj.serviceParams = serviceParams
        return obj

    # get buffer of defined BufPos
    def getBufPos(self, obj):
        print("[SERVICEORDERHANDLER] Request GetBufPos")
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
                pass
            # PLC is robotino or branch
            elif resourceId != 1:
                if bufPos == 1 and bufNo == 1:
                    if plcBuf.buffOut:
                        obj.pNo = 25
                        obj.boxPNo = 25
                        obj.oNo = plcBuf.bufOutONo
                        obj.oPos = plcBuf.bufOutOPos
                    else:
                        obj.pNo = 0
                        obj.oNo = 0
                        obj.oPos = 0
                elif bufPos == 2 and bufNo == 1:
                    if plcBuf.buffIn:
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
        print("[GETBUFPOS] Returned buffer to resource " + str(resourceId))
        return obj

    # get buffer from the docked AGV
    def getBufDockedAgv(self, obj):
        print("[SERVICEORDERHANDLER] Request GetBufDockedAgv")
        requestId = obj.requestID
        plc = StatePLC.objects.all().filter(dockedAt=requestId)
        if plc.count() == 1:
            obj.resourceId = plc.first().id

        # bufNo and bufPos are always 1
        obj.bufNo = 1
        obj.bufPos = 1
        obj.pNo = 25

        # check if a workingpiece is on the robotino
        stateWorkingPiece = StateWorkingPiece.objects.all().filter(
            location=obj.resourceId)
        if stateWorkingPiece.count() == 1:
            # only set if a carrier is on the robotino
            buffer = StatePLC.objects.all().filter(dockedAt=requestId).first().buffer
            obj.oNo = buffer.bufOutONo
            obj.oPos = buffer.bufOutOPos
        else:
            obj.oNo = 0
            obj.oPos = 0
        print(
            "[GETBUFDOCKEDAGV] Returned buffer of docked AGV to resource " + str(requestId))
        return obj

    # move a buffer from source to target (for buffer and FIFO)
    def moveBuf(self, obj):
        print("[SERVICEORDERHANDLER] Request MoveBuf")
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
            originPlc = originPlc.first()
            targetPlc = targetPlc.first()
            oldbuffer = originPlc.buffer
            targetbuffer = targetPlc.buffer
            # update target buffer
            if newBufNo == 1:
                targetbuffer.update(bufferOut=True)
                targetbuffer.update(bufOutONo=oldbuffer.bufOutONo)
                targetbuffer.update(bufOutOPos=oldbuffer.bufOutOPos)
            elif newBufNo == 2:
                targetbuffer.update(bufferIn=True)
                targetbuffer.update(bufInONo=oldbuffer.bufInONo)
                targetbuffer.update(bufInOPos=oldbuffer.bufInOPos)
        # update origin buffer
            if oldBufNo == 1:
                oldbuffer.update(bufferOut=False)
                oldbuffer.update(bufOutONo=0)
                oldbuffer.update(bufOutOPos=0)
            elif oldBufNo == 2:
                oldbuffer.update(bufferIn=False)
                oldbuffer.update(bufInONo=0)
                oldbuffer.update(bufInOPos=0)
        print("[MOVEBUF] Moved buffer from resource " +
              str(oldId) + " to resource " + str(newId))

        # set output parameter
        obj.serviceParams = []
        obj.dataLength = 0
        return obj

    # write in buffer; Aux1Int = Qunatity of a stack buffer
    def setBufPos(self, obj):
        print("[SERVICEORDERHANDLER] Request SetBufPos")
        # get input parameter
        resourceId = obj.resourceId
        bufNo = obj.bufNo
        bufPos = obj.bufPos
        partNo = obj.pNo
        oNo = obj.oNo
        oPos = obj.oPos

        # update workingpiece(location) and plc(buffer)
        stateWorkingPiece = StateWorkingPiece.objects.all().filter(
            location=obj.resourceId)
        if stateWorkingPiece.count() == 1:
            stateWorkingPiece = stateWorkingPiece.first()
            stateWorkingPiece.update(location=resourceId)
        statePlc = StatePLC.objects.all().filter(id=obj.resourceId)
        if statePlc.count() == 1:
            statePlc = statePlc.first()
            # stateWorkingPiece.update()
            # PLC isnt storage
            if resourceId != 1:
                if bufNo == 1:
                    if partNo != 0:
                        buffer = statePlc.buffer
                        buffer.update(bufferOut=True)
                        buffer.update(bufOutONo=oNo)
                        buffer.update(bufOutOPos=oPos)
                    elif partNo == 0:
                        buffer = statePlc.buffer
                        buffer.update(bufferOut=False)
                        buffer.update(bufOutONo=0)
                        buffer.update(bufOutOPos=0)
                elif bufNo == 2:
                    if partNo != 0:
                        buffer = statePlc.buffer
                        buffer.update(bufferIn=True)
                        buffer.update(bufInONo=oNo)
                        buffer.update(bufInOPos=oPos)
                    elif partNo == 0:
                        buffer = statePlc.buffer
                        buffer.update(bufferIn=False)
                        buffer.update(bufferInONo=0)
                        buffer.update(bufferInOPos=0)
            # PLC is storage
            elif resourceId == 1:
                if bufNo == 1:
                    if partNo != 0:
                        Setting.objects.all().first().updateStoragePosition(bufPos, False)
                    elif partNo == 0:
                        Setting.objects.all().first().updateStoragePosition(bufPos, True)

        # system return all parameter as 0
        obj.resourceId = 0
        obj.bufNo = 0
        obj.bufPos = 0
        obj.pNo = 0
        obj.oNo = 0
        obj.oPos = 0
        obj.palletID = 0
        obj.boxId = 0
        print("[SETBUFPOS] Buffer for resource " + str(resourceId) + " set")
        return obj

    # delete all positions of a defined buffer
    def delBuf(self, obj):
        print("[SERVICEORDERHANDLER] Request DelBuf")
        resourceId = obj.resourceId
        bufNo = obj.bufNo

        # delete buffer/ reset buffer
        plc = StatePLC.objects.all().filter(id=resourceId)
        if plc.count() == 1:
            plc = plc.first()
            buffer = Buffer.objects.all().filter(resourceId=plc.id)
            if bufNo == 1:
                print("[DELBUF] Delete bufferOut of resource " + str(resourceId))
                buffer.update(bufferOut=False)
                buffer.update(bufOutONo=0)
                buffer.update(bufOutOPos=0)
            elif bufNo == 2:
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
        print("[SERVICEORDERHANDLER] Request GetUnknownParts")
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
        print("[SERVICEORDERHANDLER] Request GetToAGVBuf")
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
                    targetId = workingSteps[i].assignedToUnit
                    if i > 1:
                        startId = workingSteps[i-1].assignedToUnit
                    else:
                        startId = targetId
                    print("[GETTOAGVBUF] Found start " + str(startId) +
                          " and target " + str(targetId)+" for Robotinos")
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
        self.serviceParams = answerParameterlist
        return obj

    # write the actuall AGV Position Aux1Int = AgvId
    def setAgvPos(self, obj):
        print("[SERVICEORDERHANDLER] Request SetAgvPos")
        # input parameter
        robotinoId = obj.aux1Int
        dockedAt = obj.resourceId

        # update resource id where robotino is docked
        robotino = StatePLC.objects.all().filter(id=robotinoId)
        if robotino.count() == 1:
            robotino = robotino
            robotino.update(dockedAt=dockedAt)
            print("[SETAGVPOS] Robotino with id " + str(robotinoId) +
                  " docked at resource " + str(dockedAt))

        # set output parameter
        obj.aux1Int = 0
        obj.resourceId = 0
        return obj
