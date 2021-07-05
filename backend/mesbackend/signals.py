"""
Filename: signals.py
Version name: 0.1, 2021-05-19
Short description: Signals that trigger callbackfunctions on certain triggers. Only handles signals which do buisness logic,
callback functions for data managment pruposes are defined in the signals of mesapi

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

from django.db.models.signals import post_save, pre_save, pre_delete, post_delete, m2m_changed
from django.dispatch import receiver
from django.db import transaction
from django.utils import tree
from threading import Thread
import requests
import logging

from .safteymonitoring import SafteyMonitoring
from mesapi.models import Error, AssignedOrder, StateVisualisationUnit, WorkingPlan, WorkingStep, Setting


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

    errorStr = instance.level + " " + instance.category + ": " + instance.msg
    if instance.level == "[WARNING]":
        logger.warning(errorStr)
    elif instance.level == "[ERROR]":
        logger.error(errorStr)
    elif instance.level == "[CRITICAL]":
        logger.critical(errorStr)

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


# Gets executed after a workingplan is saved. It validates the workingplan if it is executable
@receiver(m2m_changed, sender=WorkingPlan.workingSteps.through)
def validateWorkingPlan(sender, instance, **kwargs):
    print("[VALIDATING] Validate workingplan")
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
# workingSteps: sorted List of the workingsteps in the workingplan which needs to be checked
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
