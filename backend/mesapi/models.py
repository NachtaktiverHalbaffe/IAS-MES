"""
Filename: models.py
Version name: 0.1, 2021-05-14
Short description: Data model definitions of the backend. All datamodels are defined here

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

from django.db import models
from django.db.models.base import Model
from django.db.models.deletion import CASCADE
from django.db.models.fields import CharField, DateField
from colorfield.fields import ColorField
import json


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
    # buffer number
    buffNo = models.PositiveIntegerField(default=0)
    # buffer position
    buffPos = models.PositiveIntegerField(default=0)

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
    # timestamp of last update. Will be auto generated
    lastUpdate = models.DateTimeField(auto_now_add=True)
    # ressourceID where the working piece is currently located
    location = models.PositiveSmallIntegerField(default=1)
    # part number
    partNo = models.PositiveIntegerField(default=210)
    # id of the carrier where the (fictive) wokring piece is located
    carrierId = models.PositiveSmallIntegerField(primary_key=True)
    # ressourceID of the ressource. Shouldnt be mistaken with the ressource id of the PLC
    ressourceId = models.PositiveSmallIntegerField()
    # color of the working piece
    color = ColorField()
    # working piece is in assembled state
    isAssembled = models.BooleanField()
    # working piece is packaged
    isPackaged = models.BooleanField()

    def __str__(self):
        return str(self.partNo)
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
    stepNo = models.PositiveSmallIntegerField(primary_key=True)
    # operation number, see CP Factory documentation
    operationNo = models.PositiveSmallIntegerField(default=510)

    def __str__(self):
        return self.name + " (Step Number: " + str(self.stepNo) + ")"

# Model of a working plan. Working order define the production process of an order


class WorkingPlan(models.Model):
    name = models.CharField(max_length=30)
    description = models.CharField(max_length=200, default="")
    # number of the workingplan
    workingPlanNo = models.PositiveSmallIntegerField(primary_key=True)
    workingSteps = models.ManyToManyField(WorkingStep)

    def __str__(self):
        return self.name

# Model representing a Order which is assigned by the user


class AssignedOrder(models.Model):
    # name of the working plan
    name = models.CharField(max_length=30)
    # short description of working plan (optional)
    description = models.CharField(max_length=200, default="")
    # Workingplan which should be executed
    assigendWorkingPlan = models.ForeignKey(
        WorkingPlan, on_delete=models.CASCADE)
    # timestamp when it was assigned. Gets auto generated
    assignedAt = models.DateTimeField(auto_now_add=True)
    # order number
    orderNo = models.PositiveIntegerField(primary_key=True)
    # order psoition (optional)
    orderPos = models.PositiveSmallIntegerField(default=0)
    # main order position (optional)
    mainOrderPos = models.PositiveSmallIntegerField(default=0)
    # costumer number (optional)
    costumerNo = models.PositiveIntegerField(default=1000)
    # Status
    status = models.CharField(max_length=30, null=True)

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
    # if tcp connections are forwared to mes4
    isInBridgingMode = models.BooleanField()
    # ip adress of mes4
    ipAdressMES4 = models.GenericIPAddressField()

    def __str__(self):
        return " "


# model representing a costumer
class Costumer(models.Model):
    # costumer number which identifies the costumer. needs to be unique
    costumerNo = models.PositiveIntegerField(primary_key=True)
    firstName = models.CharField(max_length=30)
    lastName = models.CharField(max_length=100)
    adress = models.CharField(max_length=300, null=True)
    phone = models.PositiveIntegerField(null=True)
    eMail = models.EmailField(null=True)
    company = models.CharField(max_length=100, null=True)

    def __str__(self):
        return self.firstName + self.lastName
