"""
Filename: handleerrors.py
Version name: 0.1, 2021-06-15
Short description: Functions which handles the errors itself

(C) 2003-2021 IAS, Universitaet Stuttgart

"""
from backend.mesapi.models import WorkingPlan, WorkingStep, StateVisualisationUnit
from mesapi.models import AssignedOrder, Error
from .signals import _validateWorkingSteps
from .safteymonitoring import SafteyMonitoring

import requests

# handle error when visualisation unit isnt reachable


def vsNotReachable(id, oNo, oPos):
    order = AssignedOrder.objects.filter(
        orderNo=oNo).filter(orderPos=oPos)
    status = order.getStatus()
    steps = order.first().assigendWorkingPlan.workingSteps.all()
    if not _validateUpdatedOrder(steps=steps, order=order, status=status):
        safteyMonitoring = SafteyMonitoring()
        safteyMonitoring.decodeError(
            errorLevel=safteyMonitoring.LEVEL_WARNING,
            errorCategory=safteyMonitoring.CATEGORY_OPERATIONAL,
            msg="Due to update of the order because of an unreachable visualisationunit the order isnt executable anymore. Order got deleted"
        )
    Error.objects.filter(id=id).update(isSolved=True)


# handle error when visualisation unit has aborted an task
def vsAbortedProcessVisualisation(id, boundToResource):
    currentOrder = AssignedOrder.objects.all()
    for order in currentOrder:
        workingPlan = order.assigendWorkingPlan
        status = order.getStatus()
        workingSteps = workingPlan.workingSteps
        for i in range(len(status)):
            if workingSteps[i].assignedToUnit == boundToResource:
                # validate workingplan if status is already finished
                if status[i] == 1:
                    AssignedOrder.objects.filter(orderNo=order.orderNo).filter(
                        orderPos=order.oPos).update(status=status)
                    # validate if new steps are executbale
                    if not _validateUpdatedOrder(steps=workingSteps, order=order, status=status):
                        safteyMonitoring = SafteyMonitoring()
                        safteyMonitoring.decodeError(
                            errorLevel=safteyMonitoring.LEVEL_WARNING,
                            errorCategory=safteyMonitoring.CATEGORY_OPERATIONAL,
                            msg="Due to update of the order because of an aborted processvisualisation on a visualisationunit the order isnt executable anymore. Order got deleted"
                        )
                    break
                # send visualisationtask again
                elif status[i] == 0:
                    payload = {
                        "task": workingSteps[i].task,
                        "assignedWorkingPiece": order.assignedWorkingPiece,
                        "stepNo": workingSteps[i].stepNo,
                        "paintColor": workingSteps[i].color
                    }
                    ipAdress = StateVisualisationUnit.objects.filter(
                        boundToRessource=boundToResource).ipAdress
                    try:
                        request = requests.put("http://" +
                                               ipAdress + ':2000/api/VisualisationTask', data=payload)
                        if not request.ok:
                            # Error message
                            safteyMonitoring = SafteyMonitoring()
                            safteyMonitoring.decodeError(
                                errorLevel=safteyMonitoring.LEVEL_ERROR,
                                errorCategory=safteyMonitoring.CATEGORY_CONNECTION,
                                msg="Visualisation unit is not reachable. Check connection of the unit to the MES. Ordernumber and orderposition:" +
                                    str(order.orderNo) + ":" +
                                str(order.orderPos)
                            )
                            status[i] = 1
                            order.setStatus(status)
                    except Exception as e:
                        safteyMonitoring = SafteyMonitoring()
                        safteyMonitoring.decodeError(
                            errorLevel=safteyMonitoring.LEVEL_ERROR,
                            errorCategory=safteyMonitoring.CATEGORY_CONNECTION,
                            msg=str(e)
                        )
                        status[i] = 1
                        order.setStatus(status)
                    break
    Error.objects.filter(id=id).update(isSolved=True)


# validate if an updated order due to an error is still executable
def _validateUpdatedOrder(steps, order, status):
    updatedSteps = []
    # create updated list of workingsteps which are reachaböe
    for i in range(len(steps)):
        if status[i] == 0:
            updatedSteps.append(steps[i])
    # validate new workingsteps
    isExecutable = _validateWorkingSteps(workingSteps=updatedSteps)
    if not isExecutable:
        # delete order because it isnt executable
        order.delete()
        return False
    else:
        return True
