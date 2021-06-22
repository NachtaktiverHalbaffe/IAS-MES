"""
Filename: views.py
Version name: 0.1, 2021-05-14
Short description: Views for all url endpoints. The views are inherited from classbased GenericView
which inhertis from APIView. All the REST-Requests are handled here

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

from django.shortcuts import render
from django.http import JsonResponse

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView


from .serializers import *
from .models import *

# Overview of all API Endpoints


class APIOverview(APIView):
    def get(self, request, *args, **kwargs):
        overview = {
            "Get or Post on states of all PLC": "api/StatePLC/",
            "Get or Post on states of all Visualisationunits": "api/StateVisualisationUnit/",
            "Get or Post on all VisualisationTasks": "api/VisualisationTask/",
            "Get or Post on states of all WorkingPieces": "api/StateWorkingPiece/",
            "Get or Post on all assigned Orders": "api/AssignedOrder/",
            "Get or Post on all WorkingPlans": "api/WorkingPlan/",
            "Get or Post on all WorkingSteps": "api/WorkingStep/",
            "Get or Post on all Error": "api/Error/",
            "Get or Post on all Settings": "api/Setting/",
            "Get or Post on all Costumers": "api/Costumer/",
        }
        return Response(overview)


# ListCreateView creates view with get and post options for collection of entities
class StatePLCView(ListCreateAPIView):
    # serializer class so it can be used. needed for serializing request and responsen
    serializer_class = StatePLCSerializer
    # queryset with which the requests will be handled. All entities will be loaded into this object
    queryset = StatePLC.objects.all()


# RetrieveUpdateDestroVIew provides a view with put, patch, get and delete capabilities for single entity
class SingleStatePLCView(RetrieveUpdateDestroyAPIView):
    # serializer class so it can be used. needed for serializing request and responsen
    serializer_class = StatePLCSerializer
    # queryset with which the requests will be handled. All entities will be loaded into this object
    queryset = StatePLC.objects.all()


class BufferView(ListCreateAPIView):
    serializer_class = BufferSerializer
    queryset = Buffer.objects.all()


class SingleBuffer(RetrieveUpdateDestroyAPIView):
    serializer_class = BufferSerializer
    queryset = Buffer.objects.all()


class StateVisualisationUnitView(ListCreateAPIView):
    serializer_class = StateVisualisationUnitSerializer
    queryset = StateVisualisationUnit.objects.all()


class SingleStateVisualisationUnitView(RetrieveUpdateDestroyAPIView):
    serializer_class = StateVisualisationUnitSerializer
    queryset = StateVisualisationUnit.objects.all()


class StateWorkingPieceView(ListCreateAPIView):
    serializer_class = StateWorkingPieceSerializer
    queryset = StateWorkingPiece.objects.all()


class SingleStateWorkingPieceView(RetrieveUpdateDestroyAPIView):
    serializer_class = StateWorkingPieceSerializer
    queryset = StateWorkingPiece.objects.all()


class AssignedOrderView(ListCreateAPIView):
    serializer_class = AssignedOrderSerializer
    queryset = AssignedOrder.objects.all()


class SingleAssignedOrderView(RetrieveUpdateDestroyAPIView):
    serializer_class = AssignedOrderSerializer
    queryset = AssignedOrder.objects.all()


class WorkingPlanView(ListCreateAPIView):
    serializer_class = WorkingPlanSerializer
    queryset = WorkingPlan.objects.all()


class SingleWorkingPlanView(RetrieveUpdateDestroyAPIView):
    serializer_class = WorkingPlanSerializer
    queryset = WorkingPlan.objects.all()


class WorkingStepView(ListCreateAPIView):
    serializer_class = WorkingStepSerializer
    queryset = WorkingStep.objects.all()


class SingleWorkingStepView(RetrieveUpdateDestroyAPIView):
    serializer_class = WorkingStepSerializer
    queryset = WorkingStep.objects.all()


class ErrorView(ListCreateAPIView):
    serializer_class = ErrorSerializer
    queryset = Error.objects.all()


class SingleErrorView(RetrieveUpdateDestroyAPIView):
    serializer_class = ErrorSerializer
    queryset = Error.objects.all()


class SettingView(ListCreateAPIView):
    serializer_class = SettingSerializer
    queryset = Setting.objects.all()


class SingleSettingView(RetrieveUpdateDestroyAPIView):
    serializer_class = SettingSerializer
    queryset = Setting.objects.all()


class CostumerView(ListCreateAPIView):
    serializer_class = CostumerSerializer
    queryset = Costumer.objects.all()


class SingleCostumerView(RetrieveUpdateDestroyAPIView):
    serializer_class = CostumerSerializer
    queryset = Costumer.objects.all()

class SingleCostumerByNameView(RetrieveUpdateDestroyAPIView):
    serializer_class = CostumerSerializer
    lookup_url_kwarg = 'name'

    def get_queryset(self):
        queryset= Costumer.objects.all()
        name = self.kwargs.get(self.lookup_url_kwarg)
        firstName = name.split(" ")[0]
        lastName = name.split(" ")[1]
        print(firstName)
        print(lastName)
        costumer = queryset.filter(firstName=firstName).filter(lastName=lastName)
        return costumer
