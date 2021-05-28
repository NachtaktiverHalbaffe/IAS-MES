"""
Filename: servicecalls.py
Version name: 0.1, 2021-05-18
Short description: Module for handling the service calls. The buisness logic for each servicecall 
is handled here. Given on the servicecalls some output parameters are set

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

from backend.mesapi.models import AssignedOrder, Setting, StatePLC, WorkingPlan, WorkingStep, StateWorkingPiece


class Servicecalls(object):

    def __init__(self):
        from .systemmonitoring import SystemMonitoring
        self.systemmonitoring = SystemMonitoring()

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
        return obj

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
                        obj.oNo = 0
                        obj.oPos = 0
                        obj.stopperId = 0
        return obj

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
                        obj.stopperId = 0
                else:
                    obj.stopperId = 0

        return obj

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

    def setPar(self, obj):
        print("[SERVICEORDERHANDLER] Request SetPar")
        requestId = obj.requestId
        oNo = obj.oNo
        oPos = obj.oPos
        # Load current orders and search if theres a order according to orderNo and Opos
        currentOrder = AssignedOrder.objects.all()
        for order in currentOrder:
            if order.orderNo == oNo and order.orderPos == oPos:
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

    def opReset(self, obj):
        print("[SERVICEORDERHANDLER] Request OpReset")
        return

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
                        # Write NFC tags, data for NFC tag can be manip
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
                        obj.serviceParam = [2]
                        break
                    else:
                        obj.serviceParam = [1]
                        break
        return obj

    def getBufForBufNo(self, obj):
        print("[SERVICEORDERHANDLER] Request GetBufForBufNo")
        return

    def getBufPos(self, obj):
        print("[SERVICEORDERHANDLER] Request GetBufPos")
        return

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
            currentOrder = AssignedOrder.objects.all().first()
            obj.oNo = currentOrder.orderNo
            obj.oPos = currentOrder.orderPos
        else:
            obj.oNo = 0
            obj.oPos = 0
        return obj

    def setBufPos(self, obj):
        print("[SERVICEORDERHANDLER] Request SetBufPos")
        # get input parameter
        resourceId = obj.resourceId
        bufNo = obj.bufNo
        bufPos = obj.bufPos
        partNo = obj.pNo

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
                    statePlc.update(bufOut=True)
                elif partNo == 0:
                    statePlc.update(bufOut=False)
            elif bufNo == 2:
                if partNo != 0:
                    statePlc.update(bufIn=True)
                elif partNo == 0:
                    statePlc.update(bufIn=False)
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
        return obj

    def getToAGVBuf(self, obj):
        print("[SERVICEORDERHANDLER] Request GetToAGVBuf")
        return
