"""
Filename: servicecalls.py
Version name: 0.1, 2021-05-18
Short description: Module for handling the service calls. The buisness logic for each servicecall 
is handled here. Given on the servicecalls some output parameters are set

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

from backend.mesapi.models import AssignedOrder, WorkingPlan, WorkingStep, StateWorkingPiece


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
        resourceId = obj.resourceId
        oNo = obj.oNo
        oPos = obj.oPos
        # Load current orders and search if theres a order according to orderNo and Opos
        currentOrder = AssignedOrder.objects.all()
        for order in currentOrder:
            workingPlan = order.assigendWorkingPlan
            workingsteps = workingPlan.workingSteps
            if order.orderNo == oNo and order.orderPos == oPos:
                status = order.status
                for i in range(len(status)):
                    if status[i] == 0:
                        obj.stepNo = workingsteps[i].stepNo
                        obj.resourceId = workingsteps[i].assignedToUnit
                        obj.wpNo = workingPlan.workingPlanNo
                        obj.opNo = workingsteps[i].operationNo
                        if obj.opNo == 210:
                            obj.stopperId = 1
                            obj.serviceParams = [0, 90, 0, 1, 0, 25]
                            # obj.bufPos = #Todo get free storage position
                        elif obj.oNo == 211:
                            obj.stopperId = 2
                            # obj.bufPos = #Todo get free storage position
                        obj.cNo = order.costumerNo
                        obj.mainOPos = order.mainOrderPos
                        obj.errorStepNo = 0
                        obj.pNo = 25  # 25= pallet, 31 = carrier
                        obj.carrierId = order.assignedWorkingPiece.carrierId
                        break
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
                            obj.serviceParams = [0, 1, 0, 91, 0, 25]
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
        return

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
        return

    def setBufPos(self, obj):
        print("[SERVICEORDERHANDLER] Request SetBufPos")
        return

    def getToAGVBuf(self, obj):
        print("[SERVICEORDERHANDLER] Request GetToAGVBuf")
        return
