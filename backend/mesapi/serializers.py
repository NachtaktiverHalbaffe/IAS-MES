"""
Filename: serializers.py
Version name: 0.1, 2021-05-14
Short description: Serializers for all data models. Needed to serialize Models for e.g. JSON Responses.
Structure is the same on evry serialiser, so code will be documentet only on first one

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

from django.db.models import fields
from rest_framework import serializers

from .models import *


class StatePLCSerializer(serializers.ModelSerializer):
    class Meta:
        # defines the model which should be serialized
        model = StatePLC
        # Defines the fields of the JSON response. Should be named the same as the models Fields
        # The kind of fields is looked up in the background by the framework
        fields = (
            'state', 'lastUpdate', 'name', 'id', 'mode', 'mesMode', 'ipAdress', 'buffNo', 'buffPos'
        )


class StateVisualisationUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateVisualisationUnit
        fields = (
            'state', 'lastUpdate', 'ipAdress', 'boundToRessource', 'baseLevelHeight', 'assignedTask'
        )


class VisualisationTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = VisualisationTask
        fields = (
            'task', 'assignedUnit'
        )


class StateWorkingPieceSerializer(serializers.ModelSerializer):
    class Meta:
        model = StateWorkingPiece
        fields = (
            'state', 'lastUpdate', 'location', 'partNo', 'carrierId', 'ressourceId', 'assignedVisualisationTask', 'color', 'isAssemled', 'isPackaged'
        )


class AssignedOrderVisualiser(serializers.ModelSerializer):
    class Meta:
        model = AssignedOrder
        fields = (
            'name', 'description', 'assignedAt', 'orderNo', 'orderPos', 'mainOrderPos', 'costumerNo'
        )


class WorkingPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingPlan
        fields = (
            'name', 'description', 'workingPlanNo', 'assignedToOrder'
        )


class WorkingStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingStep
        fields = (
            'name', 'description', 'assignedToUnit', 'workingPlan', 'color', 'stepNo', 'operationNo'
        )


class ErrorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Error
        fields = (
            'level', 'msg', 'category', 'id', 'timestamp', 'isSolved'
        )


class SettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Setting
        fields = (
            'isInBridgingMode', 'ipAdressMES4'
        )


class CostumerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Costumer
        fields = (
            'costumerNo', 'firstName', 'lastName', 'adress', 'phone', 'eMail', 'company'
        )