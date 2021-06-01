"""
Filename: signals.py
Version name: 0.1, 2021-05-31
Short description: Signals that trigger callbackfunctions on certain triggers. Only callback functions for data managment and not
business logic. Signals with buisness logic are handled in the signals in mesbackend

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

from django.db.models.signals import post_save, pre_save, post_delete, m2m_changed
from django.dispatch import receiver
from django.db import transaction
import requests

from .models import AssignedOrder, Setting, StateWorkingPiece, StatePLC, Buffer


# Gets executed before a order is saved. It creates a array of
# bits according to the number of workingsteps in the workingplan
# and saves them in a array in the AssigendOrder object
@receiver(pre_save, sender=AssignedOrder)
def createStatusBits(sender, instance, **kwargs):
    statusArray = []
    for step in range(len(instance.assigendWorkingPlan.workingSteps.all())):
        statusArray.append(0)
    instance.setStatus(statusArray=statusArray)


# Sets all storage Bits to 0 for the first time when storage isnt initialise
@receiver(pre_save, sender=Setting)
def setStorage(sender, instance, **kwargs):
    if instance.storage == None:
        # initialise storage array
        storageArray = []
        for i in range(30):
            storageArray.append(0)
        instance.setStorage(storageArray)
        # set storage bits according to workingpieces
        workingPieces = StateWorkingPiece.objects.all()
        for piece in workingPieces:
            if piece.storageLocation != 0:
                instance.updateStoragePosition(piece.storageLocation, False)


# Creates a buffer if a StatePLC is created and hasnt a buffer yet
@receiver(post_save, sender=StatePLC)
def createBuffer(sender, instance, **kwargs):
    if instance.buffer == None:
        buffer = Buffer()
        buffer.resourceId = instance.id
        buffer.bufferIn = False
        buffer.bufferOut = False
        buffer.bufInONo = 0
        buffer.bufInOPos = 0
        buffer.bufOutONo = 0
        buffer.bufOutOPos = 0
        buffer.save()
        instance.buffer = buffer
