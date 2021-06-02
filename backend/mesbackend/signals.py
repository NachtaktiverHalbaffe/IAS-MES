"""
Filename: signals.py
Version name: 0.1, 2021-05-19
Short description: Signals that trigger callbackfunctions on certain triggers. Only handles signals which do buisness logic,
callback functions for data managment pruposes are defined in the signals of mesapi

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

from django.db.models.signals import post_save, pre_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.db import transaction
import requests
import logging

from .safteymonitoring import SafteyMonitoring
from mesapi.models import Error, AssignedOrder, StateVisualisationUnit, WorkingPlan, WorkingStep, Setting


# Gets executed after a error is saved. It analyses the error and decides what the system has to do
# to solve the error
@receiver(post_save, sender=Error)
def handleError(sender, instance, **kwargs):
    # print error to console and save error to log
    logging.basicConfig(filename="safteymonitoring.log",
                        level=logging.WARNING, format='[%(asctime)s ]  %(message)s')
    errorStr = instance.level + " " + instance.category + ": " + instance.msg
    print(errorStr)
    if instance.level == "[WARNING]":
        logging.warning(errorStr)
    elif instance.level == "[ERROR]":
        logging.error(errorStr)
    elif instance.level == "[CRITICAL]":
        logging.critical(errorStr)

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
        # TODO Delete workingstep from working order
        return


# Gets executed after a order is saved. It sends all visualisationunits their
# tasks
@receiver(post_save, sender=AssignedOrder)
def sendVisualisationtasks(sender, instance, **kwargs):
    workingsteps = instance.assigendWorkingPlan.workingSteps.all()

    for step in workingsteps:
        unit = step.assignedToUnit
        task = step.task
        stepNo = step.stepNo
        if StateVisualisationUnit.objects.all().filter(boundToRessource=unit).count() == 1:
            ipAdress = StateVisualisationUnit.objects.all().filter(
                boundToRessource=unit).ipAdress
            payload = {
                "task": task,
                "assignedToUnit": unit,
                "stepNo": stepNo
            }
            request = requests.put(
                ipAdress + '/api/VisualisationTask', data=payload)

            if not request.ok:
                # Error message
                safteyMonitoring = SafteyMonitoring()
                safteyMonitoring.decodeError(
                    errorLevel=safteyMonitoring.LEVEL_ERROR,
                    errorCategory=safteyMonitoring.CATEGORY_CONNECTION,
                    msg="Visualisation unit is not reachable. Check connection of the unit to the MES"
                )
        else:
            safteyMonitoring = SafteyMonitoring()
            safteyMonitoring.decodeError(
                errorLevel=safteyMonitoring.LEVEL_ERROR,
                errorCategory=safteyMonitoring.CATEGORY_DATA,
                msg="Visualisation unit is not represented in database. Please check if unit is online and connected to the MES"
            )


@receiver(post_delete, sender=AssignedOrder)
def abortOrder(sender, instance, **kwargs):
    workingsteps = instance.assigendWorkingPlan.workingSteps.all()
    for step in workingsteps:
        unit = step.assignedToUnit
        if StateVisualisationUnit.objects.all().filter(boundToRessource=unit).count() == 1:
            ipAdress = StateVisualisationUnit.objects.all().filter(
                boundToRessource=unit).ipAdress
            request = requests.delete(ipAdress + '/api/VisualisationTask')

            if not request.ok:
                # Error message
                safteyMonitoring = SafteyMonitoring()
                safteyMonitoring.decodeError(
                    errorLevel=safteyMonitoring.LEVEL_ERROR,
                    errorCategory=safteyMonitoring.CATEGORY_CONNECTION,
                    msg="Visualisation unit is not reachable. Check connection of the unit to the MES"
                )
        else:
            safteyMonitoring = SafteyMonitoring()
            safteyMonitoring.decodeError(
                errorLevel=safteyMonitoring.LEVEL_ERROR,
                errorCategory=safteyMonitoring.CATEGORY_DATA,
                msg="Visualisation unit is not represented in database. Please check if unit is online and connected to the MES"
            )


# Gets executed after a workingplan is saved. It validates the workingplan on static parameters
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
    isValid = True
    for i in range(len(workingSteps)):
        if i != 0:
            if workingSteps[i].task == 'unpackage':
                isValid = _checkUnpackage(workingSteps, isValid, i)
                if not isValid:
                    safteyMonitoring = SafteyMonitoring()
                    safteyMonitoring.decodeError(
                        errorLevel=safteyMonitoring.LEVEL_ERROR,
                        errorCategory=safteyMonitoring.CATEGORY_INPUT,
                        msg=ERROR_PRE + "task unpackage can't be run if workingpiece isnt packaged or is stored"
                    )
                    break
            elif workingSteps[i].task == 'package':
                isValid = _checkPackage(workingSteps, isValid, i)
                if not isValid:
                    safteyMonitoring = SafteyMonitoring()
                    safteyMonitoring.decodeError(
                        errorLevel=safteyMonitoring.LEVEL_ERROR,
                        errorCategory=safteyMonitoring.CATEGORY_INPUT,
                        msg=ERROR_PRE + "task package can't be run if workingpiece is already packaged or stored"
                    )
                    break
            elif workingSteps[i].task == 'assemble':
                # check condition for assemble
                isValid = _checkAssemble(workingSteps, isValid, i)
                if not isValid:
                    safteyMonitoring = SafteyMonitoring()
                    safteyMonitoring.decodeError(
                        errorLevel=safteyMonitoring.LEVEL_ERROR,
                        errorCategory=safteyMonitoring.CATEGORY_INPUT,
                        msg=ERROR_PRE + "task assemble can't be run if workingpiece is packaged or stored"
                    )
                    break
            elif workingSteps[i].task == 'color':
                # check condition for color
                isValid = _checkColor(workingSteps, isValid, i)
                if not isValid:
                    safteyMonitoring = SafteyMonitoring()
                    safteyMonitoring.decodeError(
                        errorLevel=safteyMonitoring.LEVEL_ERROR,
                        errorCategory=safteyMonitoring.CATEGORY_INPUT,
                        msg=ERROR_PRE + "task color can't be run if workingpiece is packaged or is stored"
                    )
                    break
            elif workingSteps[i].task == 'store':
                # check condition for store
                isValid = _checkStore(workingSteps, isValid, i)
                if not isValid:
                    safteyMonitoring = SafteyMonitoring()
                    safteyMonitoring.decodeError(
                        errorLevel=safteyMonitoring.LEVEL_ERROR,
                        errorCategory=safteyMonitoring.CATEGORY_INPUT,
                        msg=ERROR_PRE + "task store can't be run if workingpiece is already stored"
                    )
                    break
            elif workingSteps[i].task == 'unstore':
                # check condition for unstore
                isValid = _checkUnstore(workingSteps, isValid, i)
                if not isValid:
                    safteyMonitoring = SafteyMonitoring()
                    safteyMonitoring.decodeError(
                        errorLevel=safteyMonitoring.LEVEL_ERROR,
                        errorCategory=safteyMonitoring.CATEGORY_INPUT,
                        msg=ERROR_PRE + "task unstore can't be run if workingpiece is already unstored"
                    )
                    break
            elif workingSteps[i].task == 'generic':
                # check condition for generic
                isValid = _checkGeneric(workingSteps, False, i)
                if not isValid:
                    safteyMonitoring = SafteyMonitoring()
                    safteyMonitoring.decodeError(
                        errorLevel=safteyMonitoring.LEVEL_ERROR,
                        errorCategory=safteyMonitoring.CATEGORY_INPUT,
                        msg=ERROR_PRE +
                        "task generic (test) can't be run if workingpiece isnt assembled or is stored or packaged"
                    )
                    break
        else:
            if workingSteps[i].task == 'unstore':
                isValid = True
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


def _checkUnpackage(workingSteps, isValid, i):
    # check conditions for unpackage
    for j in range(i):
        # before unpackage the task package has to be run
        # and the package must be unstored
        if workingSteps[j].task == 'package':
            isValid = True
        elif workingSteps[j].task == 'unpackage':
            isValid = False
        elif workingSteps[j].task == 'unstore':
            isValid = True
        elif workingSteps[j].task == 'store':
            isValid = False
    return isValid


def _checkPackage(workingSteps, isValid, i):
    # check condition for package
    for j in range(i):
        # before package the workingpiece must be unstored and unpackaged
        if workingSteps[j].task == 'package':
            isValid = False
        elif workingSteps[j].task == 'unpackage':
            isValid = True
        elif workingSteps[j].task == 'unstore':
            isValid = True
        elif workingSteps[j].task == 'store':
            isValid = False
    return isValid


def _checkAssemble(workingSteps, isValid, i):
    for j in range(i):
        # the workingpiece must be unpackaged, not already assembled and unstored
        if workingSteps[j].task == 'package':
            isValid = False
        elif workingSteps[j].task == 'assemble':
            isValid = False
        elif workingSteps[j].task == 'unstore':
            isValid = True
        elif workingSteps[j].task == 'store':
            isValid = False
    return isValid


def _checkColor(workingSteps, isValid, i):
    for j in range(i):
        # the workingpiece must be unpackaged and unstored
        if workingSteps[j].task == 'package':
            isValid = False
        elif workingSteps[j].task == 'unpackage':
            isValid = True
        elif workingSteps[j].task == 'unstore':
            isValid = True
        elif workingSteps[j].task == 'store':
            isValid = False
    return isValid


def _checkStore(workingSteps, isValid, i):
    for j in range(i):
        # workingpiece must be unstored
        if workingSteps[j].task == 'unstore':
            isValid = True
        elif workingSteps[j].task == 'store':
            isValid = False
    return isValid


def _checkUnstore(workingSteps, isValid, i):
    for j in range(i):
        # workingpiece must be stored
        if workingSteps[j].task == 'unstore':
            isValid = False
        elif workingSteps[j].task == 'store':
            isValid = True
    return isValid


def _checkGeneric(workingSteps, isValid, i):
    for j in range(i):
        # workingpiece must be unstored and assembled. If generic gets changed
        # the condition checking must be updated
        if workingSteps[j].task == 'assemble':
            isValid = True
        elif workingSteps[j].task == 'unstore':
            isValid = True
        elif workingSteps[j].task == 'store':
            isValid = False
        elif workingSteps[j].task == 'package':
            isValid = False
        elif workingSteps[j].task == 'unpackage':
            isValid = True
    return isValid
