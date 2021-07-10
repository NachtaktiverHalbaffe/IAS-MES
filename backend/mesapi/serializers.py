"""
Filename: serializers.py
Version name: 1.0, 2021-07-10
Short description: Serializers for all data models. Needed to serialize Models for e.g. JSON Responses.

(C) 2003-2021 IAS, Universitaet Stuttgart

"""
from rest_framework import serializers

from .models import *

"""
Structure is the same on every serializer, so code will be documented only on first one
"""


class BufferSerializer(serializers.ModelSerializer):
    class Meta:
        # defines the model which should be serialized
        model = Buffer
        # Defines the fields of the JSON response. Should be named the same as the models Fields
        # The kind of fields is looked up in the background by the framework
        fields = (
            "resourceId",
            "bufInONo",
            "bufInOPos",
            "bufOutONo",
            "bufOutOPos",
        )


class StatePLCSerializer(serializers.ModelSerializer):
    class Meta:
        model = StatePLC
        fields = (
            "state",
            "lastUpdate",
            "name",
            "id",
            "mode",
            "mesMode",
            "ipAdress",
            "buffer",
            "dockedAt",
        )


class StateVisualisationUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateVisualisationUnit
        fields = (
            "state",
            "lastUpdate",
            "ipAdress",
            "boundToRessource",
            "baseLevelHeight",
            "assignedTask",
        )


class StateWorkingPieceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateWorkingPiece
        fields = (
            "lastUpdate",
            "location",
            "partNo",
            "carrierId",
            "id",
            "storageLocation",
            "color",
            "isAssembled",
            "isPackaged",
            "model",
        )


class AssignedOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignedOrder
        fields = (
            "id",
            "name",
            "description",
            "assigendWorkingPlan",
            "assignedWorkingPiece",
            "assignedAt",
            "orderNo",
            "orderPos",
            "mainOrderPos",
            "costumer",
            "status"
        )


class WorkingPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingPlan
        fields = ("name", "description", "workingPlanNo", "workingSteps")


class WorkingStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingStep
        fields = (
            "name",
            "description",
            "task",
            "assignedToUnit",
            "color",
            "stepNo",
            "operationNo",
            "id",
        )


class ErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Error
        fields = ("level", "msg", "category", "id", "timestamp", "isSolved")


class CostumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Costumer
        fields = (
            "costumerNo",
            "firstName",
            "lastName",
            "adress",
            "phone",
            "eMail",
            "company",
        )


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = ("useFleetmanager",)
