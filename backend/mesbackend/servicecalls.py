"""
Filename: servicecalls.py
Version name: 0.1, 2021-05-18
Short description: Module for handling the service calls. The buisness logic for each servicecall 
is handled here. Given on the servicecalls some output parameters are set

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

from backend.mesapi.models import AssignedOrder, Buffer, Setting, StatePLC, WorkingPlan, WorkingStep, StateWorkingPiece


class Servicecalls(object):

    def __init__(self):
        from .systemmonitoring import SystemMonitoring
        self.systemmonitoring = SystemMonitoring()

    # get first operation for resource
    def getFirstOpForRsc(self, obj):
        print("[SERVICEORDERHANDLER] Request GetFirstOpForRsc")
        resourceId = obj.resourceId
        print(resourceId)
        # Load current orders and determine if the ressource has a working step in it
        currentOrder = AssignedOrder.objects.all()
        hasFoundOrder = False
        for order in currentOrder:
            workingPlan = order.assigendWorkingPlan
            workingsteps = workingPlan.workingSteps
            for step in workingsteps:
                if step.assignedToUnit == resourceId:
                    print(
                        "[GETFIRSTOPFORRSC] Found active order for resource " + str(resourceId))
                    obj.stepNo = step.stepNo
                    obj.oNo = order.orderNo
                    obj.oPos = order.orderPos
                    obj.wpNo = workingPlan.workingPlanNo
                    obj.opNo = step.operationNo
                    obj.cNo = order.costumerNo
                    obj.mainOPos = order.mainOrderPos
                    obj.errorStepNo = 0
                    obj.pNo = 25  # 25= pallet, 31 = carrier
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
        # Load current orders and search if theres a order according to orderNo and Opos
        currentOrder = AssignedOrder.objects.all().filter(
            orderNo=oNo).filter(orderPos=oPos)
        if currentOrder.count() == 1:
            workingPlan = currentOrder.assigendWorkingPlan
            workingsteps = workingPlan.workingSteps
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
                        if obj.opNo == 210:
                            obj.stopperId = 1
                            obj.serviceParams = [0, 90, 0, 1, 0, 25]
                            obj.bufPos = Setting.objects.all().first().getFirstFreePlace()
                        elif obj.oNo == 211:
                            obj.stopperId = 2
                            obj.serviceParams = [0, 1, 0, 90, 0, 25]
                            obj.bufPos = Setting.objects.all().first().getFirstFreePlace()
                        obj.cNo = currentOrder.costumerNo
                        obj.mainOPos = currentOrder.mainOrderPos
                        obj.errorStepNo = 0
                        obj.pNo = 25  # 25= pallet, 31 = carrier
                        obj.carrierId = currentOrder.assignedWorkingPiece.carrierId
                        obj.serviceParams = [0, 3, 0, 4,
                                             0, 25, 0, 0, 0, 0, 0, 0, 0, 0]
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
            workingsteps = workingPlan.workingSteps
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
                        obj.cNo = order.costumerNo
                        obj.mainOPos = order.mainOrderPos
                        obj.errorStepNo = 0
                        obj.pNo = 25  # 25= pallet, 31 = carrier
                        obj.carrierId = order.assignedWorkingPiece.carrierId
                        obj.bufNo = 1
                        break
                    else:
                        print("[GETOPFORASRS] No active order for ASRS found")
                        obj.stopperId = 0
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
        order = AssignedOrder.objects.all.filter(
            orderNo=oNo).filter(orderPos=oPos).first()
        step = order.assigendWorkingPlan.workingSteps.filter(
            assignedToUnit=requestId).first()

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
        obj.stepNo = str(step.stepNo)
        obj.serviceParams = serviceParams
        return obj

    # set parameters on runtime
    def setPar(self, obj):
        print("[SERVICEORDERHANDLER] Request SetPar")
        requestId = obj.requestId
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
        requestId = obj.requestId
        oNo = obj.oNo
        oPos = obj.oPos
        # Load current orders and search if theres a order according to orderNo and Opos
        currentOrder = AssignedOrder.objects.all().filter(
            orderNo=oNo).filter(orderPos=oPos)
        if currentOrder.count() == 1:
            # TODO update states if necessary
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
        # TODO update state update stuff
        requestId = obj.requestId
        oNo = obj.oNo
        oPos = obj.oPos
        # TODO checking with visualisation unit
        currentOrder = AssignedOrder.objects.all()
        hasFoundOrder = False
        for order in currentOrder:
            if oNo == order.orderNo and oPos == order.orderPos:
                workingPlan = order.assigendWorkingPlan
                workingsteps = workingPlan.workingSteps
                status = order.status
                for i in range(len(status)):
                    if status[i] == 0:
                        # Write NFC tags, data for NFC tag can be manipulated
                        print("[OPEND] Operation " + str(obj.opNo) + " on resource " +
                              str(requestId) + " ended. Writing next operation on RFID")
                        obj.oNo = order.orderNo
                        obj.oPos = order.orderPos
                        obj.stepNo = workingsteps[i+1].stepNo
                        obj.stepNo = 0
                        obj.resourceId = workingsteps[i+1].assignedToUnit
                        obj.wpNo = workingPlan.workingPlanNo
                        obj.opNo = workingsteps[i+1].operationNo
                        obj.cNo = order.costumerNo
                        obj.mainOPos = order.mainOrderPos
                        obj.errorStepNo = 0
                        obj.pNo = 25  # 25= pallet, 31 = carrier
                        obj.carrierId = order.assignedWorkingPiece.carrierId
                        status[i] = 1
                        order.setStatus(status)
                        hasFoundOrder = True
                        break
            if hasFoundOrder:
                # has found order, only first order is requested => exit
                break
        return obj

    # get shunt for target resource
    def getShuntForTarget(self, obj):
        print("[SERVICEORDERHANDLER] Request GetShuntForTarget")
        requestID = obj.requestID
        currentOrder = AssignedOrder.objects.all()
        for order in currentOrder:
            workingPlan = order.assigendWorkingPlan
            workingsteps = workingPlan.workingSteps
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
        # PLC is storage
        if resourceId == 1:
            pass
        # PLC is robotino or branch
        elif resourceId != 1:
            if bufNo == 1:
                if plcBuf.bufferOut:
                    # TODO check TCP dump for message format
                    # obj.oNo =
                    # obj.oPos =
                    obj.pNo = 25
                else:
                    obj.pNo = 0
            elif bufNo == 2:
                if plcBuf.bufferIn:
                    # obj.oNo =
                    # obj.oPos =
                    obj.pNo = 25
                else:
                    obj.pNo = 0
        print("[GETBUFFORBUFNO] Returned buffer to resource " + str(resourceId))
        return obj

    # get buffer of defined BufPos
    def getBufPos(self, obj):
        print("[SERVICEORDERHANDLER] Request GetBufPos")
        # get input parameter
        resourceId = obj.resourceId
        bufNo = obj.bufNo
        bufPos = obj. bufPos

        # get output parameter
        plc = StatePLC.objects.all().filter(id=resourceId).first()
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
                    obj.oNo = plcBuf.bufOutONo
                    obj.oPos = plcBuf.bufOutOPos
                else:
                    obj.pNo = 0
                    obj.oNo = 0
                    obj.oPos = 0
            elif bufPos == 2 and bufNo == 1:
                if plcBuf.buffIn:
                    obj.pNo = 25
                    obj.oNo = plcBuf.bufInONo
                    obj.oPos = plcBuf.bufOutOPos
                else:
                    obj.pNo = 0
                    obj.oNo = 0
                    obj.oPos = 0
        print("[GETBUFPOS] Returned buffer to resource " + str(resourceId))
        return obj

    # get buffer from the docked AGV
    def getBufDockedAgv(self, obj):
        print("[SERVICEORDERHANDLER] Request GetBufDockedAgv")
        requestId = obj.requestID
        obj.resourceId = StatePLC.objects.all().filter(dockedAt=requestId).first().id

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
            location=obj.resourceId).first()
        stateWorkingPiece.update(location=resourceId)
        statePlc = StatePLC.objects.all().filter(id=obj.resourceId).first()
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

    # get a buffer where a AGV can get a defined Part
    def getToAGVBuf(self, obj):
        print("[SERVICEORDERHANDLER] Request GetToAGVBuf")
        return
