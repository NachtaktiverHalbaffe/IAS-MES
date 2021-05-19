"""
Filename: signals.py
Version name: 0.1, 2021-05-19
Short description: Signals that trigger callbackfunctions on certain triggers

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .safteymonitoring import SafteyMonitoring
from mesapi.models import Error, AssignedOrder, WorkingPlan


# Gets executed when a error is saved. It analyses the error and decides what the system has to do
# to solve the error
@receiver(post_save, sender=Error)
def handleError(sender, instance, **kwargs):
    print(instance.level + " " + instance.category + ": " + instance.msg)


@receiver(pre_save, sender=AssignedOrder)
def createStatusBits(sender, instance, **kwargs):
    statusArray = []
    for step in range(len(instance.assigendWorkingPlan.workingSteps.all())):
        statusArray.append(1)
    instance.setStatus(statusArray=statusArray)
