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
def createStatusBits(sender, instance, **kwargs):
    if instance.status == None:
        statusArray = []
        for step in range(len(instance.assigendWorkingPlan.workingSteps.all())):
            statusArray.append(0)
        instance.setStatus(statusArray=statusArray)
        logger.info("[AssignedOrder] Created order " + str(instance.orderNo) + " with workingplan " +
                    str(instance.assigendWorkingPlan.workingPlanNo)
                    )


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
