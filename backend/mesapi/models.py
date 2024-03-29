"""
Filename: models.py
Version name: 1.0, 2021-07-10
Short description: Data model definitions of the backend. All datamodels are defined here

(C) 2003-2021 IAS, Universitaet Stuttgart

"""
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.base import Model
from django.db.models.deletion import CASCADE
from django.db.models.fields import CharField, DateField
from colorfield.fields import ColorField
import json


class Buffer(models.Model):
    # resourceId of buffer
    resourceId = models.PositiveSmallIntegerField(primary_key=True)
    # buffer position of buffer in
    bufInONo = models.PositiveSmallIntegerField(default=0)
    bufInOPos = models.PositiveSmallIntegerField(default=0)
    # buffer position of buffer out
    bufOutONo = models.PositiveSmallIntegerField(default=0)
    bufOutOPos = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return "Buffer of resourceId " + str(self.resourceId)


# Model representing the state of an PLC
class StatePLC(models.Model):
    # state string which describes the state
    state = models.CharField(max_length=30)
    # timestamp of last update. Will be auto generated
    lastUpdate = models.DateTimeField()
    # name of the PLC, optional field
    name = models.CharField(max_length=30, default="")
    # ressourceID of the PLC. Mes identifies PLC with combination of ressourceID and ip-adress
    id = models.PositiveSmallIntegerField(primary_key=True)
    # wether the plc is in default or automatic mode
    mode = models.CharField(max_length=10)
    # if plc is in mes mode
    mesMode = models.BooleanField()
    # ip adress of the PLC
    ipAdress = models.GenericIPAddressField()
    # buffer input
    buffer = models.OneToOneField(Buffer, on_delete=models.SET_NULL, null=True)
    # if plc is robotino this is the id of the station where the robotino is docked
    dockedAt = models.PositiveSmallIntegerField(null=True)

    def __str__(self):
        return self.name


# Model representing the state of a visualisation unit
class StateVisualisationUnit(models.Model):
    # state string which describes the state
    state = models.CharField(max_length=30)
    # timestamp of last update. Will be auto generated
    lastUpdate = models.DateTimeField(auto_now_add=True)
    # ip adress of the PLC
    ipAdress = models.GenericIPAddressField()
    # ressourceID from the unit where the visualisation unit is mounted
    boundToRessource = models.PositiveSmallIntegerField(primary_key=True)
    # distance from ultrasonic sensors when theres no corrier or somethink like that underneath it
    baseLevelHeight = models.DecimalField(decimal_places=2, max_digits=5)
    # current assigned Visualisationtask
    assignedTask = models.CharField(max_length=10, default="None")

    def __str__(self):
        return str(self.boundToRessource)


# model representing the state of a working piece. Usually the working piece is fictive and
# is represented by an empty carrier in the real world
class StateWorkingPiece(models.Model):
    MODEL_CHOICES = [
        ('IAS-Logo', "Model of the IAS-logo"),
    ]
    # timestamp of last update. Will be auto generated
    lastUpdate = models.DateTimeField(auto_now_add=True)
    # ressourceID where the working piece is currently located
    location = models.PositiveSmallIntegerField(default=1)
    # part number
    partNo = models.PositiveIntegerField(default=25)
    # id of the carrier where the (fictive) wokring piece is located
    carrierId = models.PositiveSmallIntegerField(null=True)
    # id
    id = models.BigAutoField(primary_key=True)
    # location in storage location=0 : isnt in storage
    storageLocation = models.PositiveSmallIntegerField(default=0)
    # color of the working piece
    color = ColorField()
    # working piece is in assembled state
    isAssembled = models.BooleanField(default=False)
    # working piece is packaged
    isPackaged = models.BooleanField(default=False)
    # model name of 3D Model
    model = models.CharField(
        max_length=100, choices=MODEL_CHOICES, default='IAS-Logo')

    def __str__(self):
        return str(self.id)


# Model of a single task in a working plan. represents one step in a working plan
class WorkingStep(models.Model):
    TASK_CHOICES = [
        ("assemble", "Assemble the workingpiece"),
        ("package", "Package the workingpiece"),
        ("unpackage", "Unpackage the workingpiece"),
        ("color", "Paint the workingpiece"),
        ("generic", "Own implementation of a task"),
        ("store", "Store a workingpiece"),
        ("unstore", "Unstore a workingpiece"),
    ]
    MANUAL = 510
    UNSTORE = 213
    STORE = 210
    OP_CHOICES = [
        (MANUAL, 'Manual work'),
        (UNSTORE, "release a defined part on stopper 2"),
        (STORE, "store a part from stopper 1"),
    ]

    name = models.CharField(max_length=30)
    description = models.CharField(max_length=200, default="")
    # task which the visualisation unit should display
    task = models.CharField(
        max_length=15, choices=TASK_CHOICES, default="assemble")
    # ressourceID of assigned unit which should execute the task
    assignedToUnit = models.PositiveIntegerField()
    # if task is painting
    color = ColorField(default="#000000")
    # step number inside the Workingplan
    stepNo = models.PositiveSmallIntegerField()
    # operation number, see CP Factory documentation
    operationNo = models.PositiveSmallIntegerField(
        default=510, choices=OP_CHOICES)
    # id
    id = models.BigAutoField(primary_key=True)

    class Meta:
        ordering = ['stepNo']
        unique_together = ('id', 'stepNo')

    def __str__(self):
        return self.name + " (Step Number: " + str(self.stepNo) + ")"


# Model of a working plan. Working order define the production process of an order
class WorkingPlan(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=200, default="")
    # number of the workingplan
    workingPlanNo = models.PositiveSmallIntegerField(primary_key=True)
    workingSteps = models.ManyToManyField(WorkingStep, blank=True)

    def __str__(self):
        return self.name


# model representing a Customer
class Customer(models.Model):
    # Customer number which identifies the Customer. needs to be unique
    customerNo = models.PositiveIntegerField(primary_key=True)
    firstName = models.CharField(max_length=30)
    lastName = models.CharField(max_length=100)
    adress = models.CharField(max_length=300, null=True)
    phone = models.CharField(max_length=30, null=True)
    eMail = models.EmailField(null=True)
    company = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.firstName + self.lastName


# Model representing a Order which is assigned by the user
class AssignedOrder(models.Model):
    id = models.AutoField(primary_key=True)
    # name of the working plan
    name = models.CharField(max_length=30, null=False)
    # short description of working plan (optional)
    description = models.CharField(max_length=200, default="")
    # Workingplan which should be executed
    assigendWorkingPlan = models.ForeignKey(
        WorkingPlan, on_delete=models.CASCADE, null=True)
    # Assigned workingpiece
    assignedWorkingPiece = models.ForeignKey(
        StateWorkingPiece, on_delete=models.CASCADE, null=True)
    # timestamp when it was assigned. Gets auto generated
    assignedAt = models.DateTimeField(auto_now_add=True)
    # order number
    orderNo = models.PositiveIntegerField()
    # order psoition (optional)
    orderPos = models.PositiveSmallIntegerField()
    # main order position (optional)
    mainOrderPos = models.PositiveSmallIntegerField(default=0)
    # Customer(optional)
    customer = models.ForeignKey(
        Customer, blank=True, on_delete=models.SET_NULL, null=True)
    # Status
    status = models.CharField(max_length=30, null=True)

    class Meta:
        unique_together = ('orderNo', 'orderPos')

    # getter and setter for status cause it needs to be converted to string and vise versa
    def setStatus(self, statusArray):
        self.status = json.dumps(statusArray)

    def getStatus(self):
        return json.loads(self.status)

    def __str__(self):
        return self.name


# Model for safteymonitoring. Errors are stored and handled in this format
class Error(models.Model):
    ERROR_LEVEL = [
        ("[WARNING]", "Warning Level"),
        ("[ERROR]", "Error Level"),
        ("[CRITICAL]", "Critical Level"),
    ]
    ERROR_CATEGORY = [
        (
            "Connection issues",
            "Issues related to network communication and connections",
        ),
        ("Invalid input", "Issues related to invalid inputs or invalid input Data"),
        ("Operational issue", "Issues related to operating the system"),
        (
            "Integrity & Consistency issue",
            "Issues related to integrity and consitency of data",
        ),
        ("Unkown", "Unkown Error"),
    ]
    # level of the Error. See componentspecifiaction for details
    level = models.CharField(
        max_length=10, choices=ERROR_LEVEL, default="[WARNING]")
    # message of the error. See componentspecifiaction for details
    msg = models.CharField(max_length=200)
    # category of the error. See componentspecifiaction for details
    category = models.CharField(
        max_length=30, choices=ERROR_CATEGORY, default="Unkown")
    # id of the error. Autogenerated
    id = models.AutoField(primary_key=True)
    # Autogenerated
    timestamp = models.DateTimeField(auto_now_add=True)
    # if error is solved. level [WARNING] is alsways solved
    isSolved = models.BooleanField()

    def __str__(self):
        return self.level + self.category + self.msg


class Setting(models.Model):
    # if fleetmanager is used
    useFleetmanager = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.pk and Setting.objects.exists():
            # if you'll not check for self.pk
            # then error will also raised in update of exists model
            raise ValidationError('There is can be only one Setting instance')
        return super(Setting, self).save(*args, **kwargs)

    def __str__(self):
        return "Setting"
