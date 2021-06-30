"""
Filename: signals.py
Version name: 0.1, 2021-05-31
Short description: Signals that trigger callbackfunctions on certain triggers. Only callback functions for data managment and not
business logic. Signals with buisness logic are handled in the signals in mesbackend

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

from django.db.models.signals import post_save, pre_delete, pre_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.db import transaction
import requests
import logging

from .models import AssignedOrder, Setting, StateWorkingPiece, StatePLC, Buffer

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
# and saves them in a array in the AssigendOrder object


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
            if step.task == "assemble" and workingPieces.filter(isAssembled= False).count() != 0:
                workingPieces = workingPieces.filter(isAssembled= False)
            # check for generic task only if 3D-Model is ias logo (default model). For diffrent 3d Model the generic task can differ
            elif step.task == "generic" and workingPieces.filter(model="IAS-Logo").filter(isAssembled= False).count() != 0 :
                workingPieces = workingPieces.filter(model="IAS-Logo").filter(isAssembled= False)
            elif step.task == "unpackage" and workingPieces.filter(isPackaged= True).count() != 0:
                workingPieces = workingPieces.filter(isPackaged= True)
            elif step.task == "package" and workingPieces.filter(isPackaged= False).count() != 0:
                workingPieces = workingPieces.filter(isPackaged= False) 
            
        assignedWorkingPiece = workingPieces.first()
        instance.assignedWorkingPiece = assignedWorkingPiece
            

@receiver(pre_delete, sender=AssignedOrder)
def logOrderDel(sender, instance, **kwargs):
    logging.basicConfig(filename="orders.log",
                        level=logging.INFO, format='[%(asctime)s ] %(name)s : %(message)s')
    logging.info("[AssignedOrder] Deleted order " + str(instance.orderNo))



# Creates a buffer if a StatePLC is created and hasnt a buffer yet
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
