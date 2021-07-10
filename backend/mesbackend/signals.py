"""
Filename: signals.py
Version name: 1.0, 2021-07-20
Short description: Signals that trigger callbackfunctions on certain triggers which gets fired when models are
modified by the orm

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

from django.db.models.signals import post_save, pre_save, pre_delete, m2m_changed
from django.dispatch import receiver
from threading import Thread
import requests
import logging

from .safteymonitoring import SafteyMonitoring
from mesapi.models import Error, AssignedOrder, StateVisualisationUnit, WorkingPlan, WorkingStep, StatePLC, Buffer, StateWorkingPiece

# setup logging
log_formatter = logging.Formatter('[%(asctime)s ] %(name)s : %(message)s')
# handler for logging to file
file_handler = logging.FileHandler("orders.log")
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.INFO)
# handler for logging to console
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)
stream_handler.setLevel(logging.INFO)
# setup logger itself
logger = logging.getLogger("orders")
logger.setLevel(logging.INFO)
# add logger handler to logger
logger.handlers = []
logger.addHandler(stream_handler)
logger.addHandler(file_handler)


# Gets executed before a order is saved. It creates a array of
# bits according to the number of workingsteps in the workingplan
# and saves them in a array in the AssigendOrder object. Also a
# workingpiece gets assigned
@receiver(pre_save, sender=AssignedOrder)
def createMissingParams(sender, instance, **kwargs):
    if instance.status == None:
        statusArray = []
        if(instance.assigendWorkingPlan != None):
            for step in range(len(instance.assigendWorkingPlan.workingSteps.all())):
                statusArray.append(0)
            instance.setStatus(statusArray=statusArray)
            logger.info("[AssignedOrder] Created order " + str(instance.orderNo) + " with workingplan " +
                        str(instance.assigendWorkingPlan.workingPlanNo)
                        )
    # assign workingpiece to order if it isnt already assigned a workingpiece
    if instance.assignedWorkingPiece == None and instance.assigendWorkingPlan != None:
        # the workingplan is already validated, so the only task is to find the first workingpiece with the right state
        # for the order to start. So for each task it is checked if a filtering would find a workingpiece. If not that means
        # that theres a workingstep before which changes the state of the workingpiece to the right state e.g. a package before a unpackage
        workingPieces = StateWorkingPiece.objects.all()
        workingSteps = instance.assigendWorkingPlan.workingSteps.all()
        for step in workingSteps:
            if step.task == "assemble" and workingPieces.filter(isAssembled=False).count() != 0:
                workingPieces = workingPieces.filter(isAssembled=False)
            # check for generic task only if 3D-Model is ias logo (default model). For diffrent 3d Model the generic task can differ
            elif step.task == "generic" and workingPieces.filter(model="IAS-Logo").filter(isAssembled=False).count() != 0:
                workingPieces = workingPieces.filter(
                    model="IAS-Logo").filter(isAssembled=False)
            elif step.task == "unpackage" and workingPieces.filter(isPackaged=True).count() != 0:
                workingPieces = workingPieces.filter(isPackaged=True)
            elif step.task == "package" and workingPieces.filter(isPackaged=False).count() != 0:
                workingPieces = workingPieces.filter(isPackaged=False)

        if(workingPieces.count() != 0):
            assignedWorkingPiece = workingPieces.first()
            instance.assignedWorkingPiece = assignedWorkingPiece
        else:
            safteyMonitoring = SafteyMonitoring()
            safteyMonitoring.decodeError(
                errorLevel=safteyMonitoring.LEVEL_ERROR,
                errorCategory=safteyMonitoring.CATEGORY_OPERATIONAL,
                msg="No workingpiece exists with the matching state to execute the order. Deleting order..."
            )
            instance.delete()


# creates and links a empty buffer to StatePLC when a instance is created
@receiver(pre_save, sender=StatePLC)
def createBuffer(sender, instance, **kwargs):
    if instance.buffer == None:
        buffer = Buffer()
        buffer.resourceId = instance.id
        buffer.bufInONo = 0
        buffer.bufInOPos = 0
        buffer.bufOutONo = 0
        buffer.bufOutOPos = 0
        buffer.save()
        instance.buffer = buffer


# Gets executed after a error is saved. It analyses the error and decides what the system has to do
# to solve the error
@receiver(post_save, sender=Error)
def handleError(sender, instance, **kwargs):
    from .handleerrors import vsNotReachable, vsAbortedProcessVisualisation

    # setup logging
    log_formatter = logging.Formatter('[%(asctime)s ] %(message)s')
    # handler for logging to file
    file_handler = logging.FileHandler("safteymonitoring.log")
    file_handler.setFormatter(log_formatter)
    file_handler.setLevel(logging.INFO)
    # handler for logging to console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_formatter)
    stream_handler.setLevel(logging.INFO)
    # setup logger itself
    logger = logging.getLogger("safteymonitoring")
    logger.setLevel(logging.INFO)
    # add logger handler to logger
    logger.handlers = []
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    # print error to logs
    errorStr = instance.level + " " + instance.category + ": " + instance.msg
    if instance.level == "[WARNING]":
        logger.warning(errorStr)
    elif instance.level == "[ERROR]":
        logger.error(errorStr)
    elif instance.level == "[CRITICAL]":
        logger.critical(errorStr)

    # errorhandling depending on errormsg
    if instance.isSolved:
        return
    # Error during validating workingplan
    elif "While saving workingplan:" in instance.msg:
        Error.objects.filter(id=instance.id).update(isSolved=True)
        return
    elif "Workingplan not saved!" in instance.msg:
        Error.objects.filter(id=instance.id).update(isSolved=True)
        return
    elif "Visualisation unit is not reachable." in instance.msg:
        params = instance.msg.split(":")
        if len(params) > 1:
            oNo = params[1]
            oPos = params[2]
        vsNotReachable(id=instance.id, oNo=oNo, oPos=oPos)
        return
    elif "Aborting processVisualisation" in instance.msg:
        params = instance.msg.split(":")
        vsAbortedProcessVisualisation(
            id=instance.id, boundToResource=params[1])


# send delete requests to all visualisationunits when a order is deleted
# (usually on end of order or if order is aborted)
@receiver(pre_delete, sender=AssignedOrder)
def deleteOrder(sender, instance, **kwargs):
    logger.info("[AssignedOrder] Deleted or finished order " +
                str(instance.orderNo))
    if instance.assigendWorkingPlan != None:
        workingsteps = instance.assigendWorkingPlan.workingSteps.all()
        for i in range(len(workingsteps)):
            step = workingsteps[i]
            unit = step.assignedToUnit
            stateVisualisationUnit = StateVisualisationUnit.objects.all().filter(
                boundToRessource=unit)
            if stateVisualisationUnit.count() == 1:
                ipAdress = stateVisualisationUnit.first().ipAdress
                Thread(target=_sendAbortVSTask, args=[ipAdress]).start()


# send delete requests to a visualisationunit when a workingstep from the resource
# bound to the unit gets deleted (assuming it happens on runtime, otherwise the delete-request
# wont do anything which means the visualisation unit does nothing)
@receiver(pre_delete, sender=WorkingStep)
def deleteWorkingStep(sender, instance, **kwargs):
    vsUnit = StateVisualisationUnit.objects.filter(
        boundToRessource=instance.assignedToUnit)
    if vsUnit.count() != 0:
        ipAdress = vsUnit.first().ipAdress
        Thread(target=_sendAbortVSTask, args=[ipAdress]).start()


# send delete requests to a old visualisationunit when a workingstep from the resource
# bound to the unit gets modified and send a put request to the new unit
@receiver(pre_save, sender=WorkingStep)
def editWorkingStep(sender, instance, **kwargs):
    # get old instance of workingstep
    try:
        oldInstance = WorkingStep.objects.get(id=instance.id)
    except WorkingStep.DoesNotExist:  # to handle initial object creation
        return None

    # check if assigned resource has changed
    if oldInstance.assignedToUnit != instance.assignedToUnit:
        # send delete request to old visualisation unit
        oldVsUnit = StateVisualisationUnit.objects.filter(
            boundToRessource=oldInstance.assignedToUnit)
        if oldVsUnit.count() != 0:
            ipAdress = oldVsUnit.first().ipAdress
            Thread(target=_sendAbortVSTask, args=[ipAdress]).start()

        # send visualisation task to new visualisation unit
        newVsUnit = StateVisualisationUnit.objects.filter(
            boundToRessource=instance.assignedToUnit)
        if newVsUnit.count() != 0:
            allOrders = AssignedOrder.objects.all()
            for order in allOrders:
                # search through all orders until modified workingstep is present in the order
                workingPlan = order.assigendWorkingPlan
                workingSteps = workingPlan.workingSteps.all()
                hasFoundOrder = False
                for i in range(len(workingSteps)):
                    if workingSteps[i].id == instance.id:
                        status = order.getStatus()
                        # check if task is first unfinished step in order => then send visualisation task
                        if status[i-1] == 1:
                            # send task to ne visualisation unit
                            Thread(target=_sendVisualisationTask, args=[
                                order.orderNo, order.orderPos, instance.assignedToUnit, instance.stepNo]).start()
                            hasFoundOrder = True
                            break
                # dont search in more orders if a visualisation task has been already send because a visualisation unit
                # can only perform one task at a time
                if hasFoundOrder == True:
                    break


# Gets executed after a workingplan is saved. It validates the workingplan if it is executable
@receiver(m2m_changed, sender=WorkingPlan.workingSteps.through)
def validateWorkingPlan(sender, instance, **kwargs):
    workingSteps = instance.workingSteps.all()
    workingSteps = workingSteps.order_by('stepNo')
    if len(workingSteps) != 0:
        isValid = _validateWorkingSteps(workingSteps)
        if not isValid:
            WorkingPlan.objects.filter(
                workingPlanNo=instance.workingPlanNo).delete()
            safteyMonitoring = SafteyMonitoring()
            safteyMonitoring.decodeError(
                errorLevel=safteyMonitoring.LEVEL_ERROR,
                errorCategory=safteyMonitoring.CATEGORY_INPUT,
                msg="Workingplan not saved!"
            )


# condition checking if all conditions are met so the workingplan can run correctly
# @param:
#   workingSteps: sorted List of the workingsteps in the workingplan which needs to be checked
def _validateWorkingSteps(workingSteps):
    ERROR_PRE = "While saving workingplan: "
    isValid = False
    errormsg = ""
    state = {
        "isPackaged": None,
        "isAssembled": None,
        "isStored": None,
    }
    for i in range(len(workingSteps)):
        if i != 0:
            if workingSteps[i].task == 'unpackage':
                isValid, errormsg, state = _checkUnpackage(
                    workingSteps, i+1, state)
                if not isValid:
                    safteyMonitoring = SafteyMonitoring()
                    safteyMonitoring.decodeError(
                        errorLevel=safteyMonitoring.LEVEL_ERROR,
                        errorCategory=safteyMonitoring.CATEGORY_INPUT,
                        msg=ERROR_PRE + errormsg
                    )
                    break
            elif workingSteps[i].task == 'package':
                isValid, errormsg, state = _checkPackage(
                    workingSteps, i+1, state)
                if not isValid:
                    safteyMonitoring = SafteyMonitoring()
                    safteyMonitoring.decodeError(
                        errorLevel=safteyMonitoring.LEVEL_ERROR,
                        errorCategory=safteyMonitoring.CATEGORY_INPUT,
                        msg=ERROR_PRE + errormsg
                    )
                    break
            elif workingSteps[i].task == 'assemble':
                # check condition for assemble
                isValid, errormsg, state = _checkAssemble(
                    workingSteps, i+1, state)
                if not isValid:
                    safteyMonitoring = SafteyMonitoring()
                    safteyMonitoring.decodeError(
                        errorLevel=safteyMonitoring.LEVEL_ERROR,
                        errorCategory=safteyMonitoring.CATEGORY_INPUT,
                        msg=ERROR_PRE + errormsg
                    )
                    break
            elif workingSteps[i].task == 'color':
                # check condition for color
                isValid, errormsg, state = _checkColor(
                    workingSteps, i+1, state)
                if not isValid:
                    safteyMonitoring = SafteyMonitoring()
                    safteyMonitoring.decodeError(
                        errorLevel=safteyMonitoring.LEVEL_ERROR,
                        errorCategory=safteyMonitoring.CATEGORY_INPUT,
                        msg=ERROR_PRE + errormsg
                    )
                    break
            elif workingSteps[i].task == 'store':
                # check condition for store
                isValid, errormsg, state = _checkStore(
                    workingSteps, i+1, state)
                if not isValid:
                    safteyMonitoring = SafteyMonitoring()
                    safteyMonitoring.decodeError(
                        errorLevel=safteyMonitoring.LEVEL_ERROR,
                        errorCategory=safteyMonitoring.CATEGORY_INPUT,
                        msg=ERROR_PRE + errormsg
                    )
                    break
            elif workingSteps[i].task == 'unstore':
                # check condition for unstore
                isValid, errormsg, state = _checkUnstore(
                    workingSteps, i+1, state)
                if not isValid:
                    safteyMonitoring = SafteyMonitoring()
                    safteyMonitoring.decodeError(
                        errorLevel=safteyMonitoring.LEVEL_ERROR,
                        errorCategory=safteyMonitoring.CATEGORY_INPUT,
                        msg=ERROR_PRE + errormsg
                    )
                    break
            elif workingSteps[i].task == 'generic':
                # check condition for generic
                isValid, errormsg, state = _checkGeneric(
                    workingSteps, i+1, state)
                if not isValid:
                    safteyMonitoring = SafteyMonitoring()
                    safteyMonitoring.decodeError(
                        errorLevel=safteyMonitoring.LEVEL_ERROR,
                        errorCategory=safteyMonitoring.CATEGORY_INPUT,
                        msg=ERROR_PRE + errormsg
                    )
                    break
        else:
            if workingSteps[i].task == 'unstore':
                isValid = True
                errormsg = ""
                state["isStored"] = False
            else:
                isValid = False
                safteyMonitoring = SafteyMonitoring()
                safteyMonitoring.decodeError(
                    errorLevel=safteyMonitoring.LEVEL_ERROR,
                    errorCategory=safteyMonitoring.CATEGORY_INPUT,
                    msg=ERROR_PRE +
                    "first task must be unstore"
                )
                break
    return isValid


"""
subfunctions for validating workingplan
"""


def _checkUnpackage(workingSteps, i, state):
    isValid = True
    errormsg = ""
    newState = state
    # check conditions for unpackage
    for j in range(i):
        # validating
        if workingSteps[j].task == 'package':
            if (newState["isPackaged"] == False):
                isValid = True
                errormsg = ""
            newState["isPackaged"] = True
        elif workingSteps[j].task == 'unpackage':
            if newState["isPackaged"] == False:
                isValid = False
                errormsg = "task package must be run before being unpackaged"
            newState["isPackaged"] = False
        elif workingSteps[j].task == 'store':
            newState["isStored"] = True
            isValid = False
            errormsg = "workingpiece must be unstored before being unpackaged"
        elif workingSteps[j].task == 'unstore':
            if newState["isStored"] == True:
                isValid = True
                errormsg = ""
            newState["isStored"] = False
        # state tracking
        elif workingSteps[j].task == 'assemble':
            newState["isAssembled"] = True
        elif workingSteps[j].task == 'generic':
            newState["isAssembled"] = False
    return (isValid, errormsg, newState)


def _checkPackage(workingSteps, i, state):
    isValid = True
    errormsg = ""
    newState = state
    # check condition for package
    for j in range(i):
        # validating
        if workingSteps[j].task == 'package':
            if newState["isPackaged"] == True:
                isValid = False
                errormsg = "task unpackaged must be run before being packaged"
            newState["isPackaged"] = True
        elif workingSteps[j].task == 'unpackage':
            if newState["isPackaged"] == True:
                isValid = True
                errormsg = ""
            newState["isPackaged"] = False
        elif workingSteps[j].task == 'store':
            newState["isStored"] = True
            isValid = False
            errormsg = "workingpiece must be unstored before being unpackaged"
        elif workingSteps[j].task == 'unstore':
            if newState["isStored"] == True:
                isValid = True
                errormsg = ""
            newState["isStored"] = False
        # state tracking
        elif workingSteps[j].task == 'assemble':
            newState["isAssembled"] = True
        elif workingSteps[j].task == 'generic':
            newState["isAssembled"] = False
    return (isValid, errormsg, newState)


def _checkAssemble(workingSteps, i, state):
    isValid = True
    errormsg = ""
    newState = state
    for j in range(i):
        # validating
        if workingSteps[j].task == 'assemble':
            if newState["isAssembled"] == True:
                isValid = False
                errormsg = "task disassemble must be run before being assembled"
            newState["isAssembled"] = True
        elif workingSteps[j].task == 'generic':
            if newState["isAssembled"] == True:
                isValid = True
                errormsg = ""
            newState["isAssemled"] = False
        elif workingSteps[j].task == 'package':
            isValid = False
            errormsg = "task unpackage must be run before being assembled"
            newState["isPackaged"] = True
        elif workingSteps[j].task == 'unpackage':
            if newState["isPackaged"] == True:
                isValid = True
                errormsg = ""
            newState["isPackaged"] = False
        elif workingSteps[j].task == 'store':
            newState["isStored"] = True
            isValid = False
            errormsg = "workingpiece must be unstored before being unpackaged"
        elif workingSteps[j].task == 'unstore':
            if newState["isStored"] == True:
                isValid = True
                errormsg = ""
            newState["isStored"] = False
    return (isValid, errormsg, newState)


def _checkGeneric(workingSteps, i, state):
    isValid = True
    errormsg = ""
    newState = state
    for j in range(i):
        # validating
        if workingSteps[j].task == 'assemble':
            if newState["isAssembled"] == False:
                isValid = True
                errormsg = ""
            newState["isAssembled"] = True
        elif workingSteps[j].task == 'generic':
            if newState["isAssembled"] == False:
                isValid = False
                errormsg = "task assemble must be run before being assembled"
            newState["isAssembled"] = False
        elif workingSteps[j].task == 'store':
            newState["isStored"] = True
            isValid = False
            errormsg = "workingpiece must be unstored before being unpackaged"
        elif workingSteps[j].task == 'unstore':
            if newState["isStored"] == True:
                isValid = True
                errormsg = ""
            newState["isStored"] = False
        elif workingSteps[j].task == 'package':
            isValid = False
            errormsg = "task unpackage must be run before being assembled"
            newState["isPackaged"] = True
        elif workingSteps[j].task == 'unpackage':
            if newState["isPackaged"] == True:
                isValid = True
                errormsg = ""
            newState["isPackaged"] = False
    return (isValid, errormsg, newState)


def _checkColor(workingSteps, i, state):
    isValid = True
    errormsg = ""
    newState = state
    for j in range(i):
        # the workingpiece must be unpackaged and unstored
        if workingSteps[j].task == 'package':
            isValid = False
            errormsg = "task unpackage must be run before being assembled"
            newState["isPackaged"] = True
        elif workingSteps[j].task == 'unpackage':
            if newState["isPackaged"] == True:
                isValid = True
                errormsg = ""
            newState["isPackaged"] = False
        elif workingSteps[j].task == 'store':
            newState["isStored"] = True
            isValid = False
            errormsg = "workingpiece must be unstored before being unpackaged"
        elif workingSteps[j].task == 'unstore':
            if newState["isStored"] == True:
                isValid = True
                errormsg = ""
            newState["isStored"] = False
        # state tracking
        elif workingSteps[j].task == 'assemble':
            newState["isAssembled"] = True
        elif workingSteps[j].task == 'generic':
            newState["isAssembled"] = False
    return (isValid, errormsg, newState)


def _checkStore(workingSteps, i, state):
    isValid = True
    errormsg = ""
    newState = state
    for j in range(i):
        # validating
        if workingSteps[j].task == 'unstore':
            if newState["isStored"] == True:
                isValid = True
                errormsg = ""
            newState["isStored"] = False
        elif workingSteps[j].task == 'store':
            if newState["isStored"] == True:
                isValid = False
                errormsg = "task unstore must be run before being stored"
            newState["isStored"] = True
        # state tracking
        elif workingSteps[j].task == 'assemble':
            newState["isAssembled"] = True
        elif workingSteps[j].task == 'generic':
            newState["isAssembled"] = False
        elif workingSteps[j].task == 'package':
            newState["isPackaged"] = True
        elif workingSteps[j].task == 'unpackage':
            newState["isPackaged"] = False
    return (isValid, errormsg, newState)


def _checkUnstore(workingSteps, i, state):
    isValid = True
    errormsg = ""
    newState = state
    for j in range(i):
        # validating
        if workingSteps[j].task == 'unstore':
            if newState["isStored"] == False:
                isValid = False
                errormsg = "task store must be run before being unstored"
            newState["isStored"] = False
        elif workingSteps[j].task == 'store':
            if newState["isStored"] == False:
                isValid = True
                errormsg = ""
            newState["isStored"] = True
        # state tracking
        elif workingSteps[j].task == 'assemble':
            newState["isAssembled"] = True
        elif workingSteps[j].task == 'generic':
            newState["isAssembled"] = False
        elif workingSteps[j].task == 'package':
            newState["isPackaged"] = True
        elif workingSteps[j].task == 'unpackage':
            newState["isPackaged"] = False
    return (isValid, errormsg, newState)


# send delete-request to visualisation unit to abort visualisation task
# @params:
#   ipAdress: ip adress of visualisation unit
def _sendAbortVSTask(ipAdress):
    try:
        request = requests.delete(
            "http://" + ipAdress + ':5000/api/VisualisationTask')
        # Error message
    except Exception as e:
        safteyMonitoring = SafteyMonitoring()
        safteyMonitoring.decodeError(
            errorLevel=safteyMonitoring.LEVEL_ERROR,
            errorCategory=safteyMonitoring.CATEGORY_CONNECTION,
            msg=str(e)
        )

# send visualisation task to visualisation unit
# @param:
#   orderNo: ordernumber of order where visualisationtask is assigned to
#   orderPos: orderposition of order where visualisationtask is assigned to
#   resourceId: Id of resource where visualisationunit should be mounted on
#   stepNo: stepNo of workingstep which the visualisation task corresponds to


def _sendVisualisationTask(orderNo, orderPos, resourceId, stepNo):
    # get task
    safteyMonitoring = SafteyMonitoring()
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
                                   StateVisualisationUnit.objects.filter(boundToRessource=resourceId).first().ipAdress + ':5000/api/VisualisationTask', data=payload)
            if not request.ok:
                safteyMonitoring.decodeError(
                    errorLevel=safteyMonitoring.LEVEL_ERROR,
                    errorCategory=safteyMonitoring.CATEGORY_CONNECTION,
                    msg="Visualisation unit is not reachable. Check connection of the unit to the MES. Ordernumber and orderposition:" +
                    str(orderNo) + ":" + str(orderPos))

        except Exception as e:
            pass
            safteyMonitoring.decodeError(
                errorLevel=safteyMonitoring.LEVEL_ERROR,
                errorCategory=safteyMonitoring.CATEGORY_CONNECTION,
                msg=str(e)
            )
