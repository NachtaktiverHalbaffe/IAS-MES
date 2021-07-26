"""
Filename: views.py
Version name: 1.0, 2021-07-10
Short description: Views for all url endpoints. The views are inherited from classbased GenericView
which inhertis from APIView. All the REST-Requests are handled here

(C) 2003-2021 IAS, Universitaet Stuttgart

"""

from django.shortcuts import render
from django.http import JsonResponse
from django.views import generic

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
            "Get or Post on all Customers": "api/Customer/",
        }
        return Response(overview)


"""
All views have the same structure, so it will be explained in detail only one time
"""

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


class CustomerView(ListCreateAPIView):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()


class SingleCustomerView(RetrieveUpdateDestroyAPIView):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()


# Getting single customer by name
class SingleCustomerByNameView(ListCreateAPIView):
    serializer_class = CustomerSerializer
    # get parameter from url
    lookup_url_kwarg = 'firstName'
    lookup_url_kwarg = 'lastName'

    def get_queryset(self):
        # Search for customer by filtering by firstName
        # and lastName which are passed from the url
        queryset = Customer.objects.all()
        firstName = self.kwargs.get("firstName")
        lastName = self.kwargs.get("lastName")
        customer = queryset.filter(
            firstName=firstName).filter(lastName=lastName)
        return customer
