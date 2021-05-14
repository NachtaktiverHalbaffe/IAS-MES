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
from rest_framework import generics, mixins


from .serializers import *
from .models import *


class APIOverview(APIView):

    def get(self, request, *args, **kwargs):
        overview = {
            'Get or Post on states of all PLC': '/api/StatePLC',
            'Get or Post on states of all Visualisationunits': '/api/StateVisualisationUnit',
            'Get or Post on all VisualisationTasks': '/api/VisualisationTask',
            'Get or Post on states of all WorkingPieces': '/api/StateWorkingPiece',
            'Get or Post on all assigned Orders': '/api/AssignedOrder',
            'Get or Post on all WorkingPlans': '/api/WorkingPlan',
            'Get or Post on all WorkingSteps': '/api/WorkingStep',
            'Get or Post on all Error': '/api/Error',
            'Get or Post on all Settings': '/api/Setting',
            'Get or Post on all Costumers': '/api/Costumer',
        }
        return Response(overview)


class StatePLCView(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.DestroyModelMixin,
                   generics.GenericAPIView):
    # serializer class so it can be used. needed for serializing request and responsen
    serializer_class = StatePLCSerializer
    # queryset with which the requests will be handled. All entities will be loaded into this object
    queryset = StatePLC.objects.all()

    def get(self, request, *args, **kwargs):
        # return repsonse with the help of the ListModelMixin Class
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        # return repsonse with the help of the CreateModelMixin Class
        return self.create(request, *args, **kwargs)


class StateVisualisationUnitView(mixins.ListModelMixin,
                                 mixins.CreateModelMixin,
                                 mixins.UpdateModelMixin,
                                 mixins.RetrieveModelMixin,
                                 mixins.DestroyModelMixin,
                                 generics.GenericAPIView):
    serializer_class = StateVisualisationUnitSerializer
    queryset = StateVisualisationUnit.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class VisualisationTaskView(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            mixins.UpdateModelMixin,
                            mixins.RetrieveModelMixin,
                            mixins.DestroyModelMixin,
                            generics.GenericAPIView):
    serializer_class = VisualisationTaskSerializer
    queryset = VisualisationTask.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class StateWorkingPieceView(mixins.ListModelMixin,
                            mixins.CreateModelMixin,
                            generics.GenericAPIView):
    serializer_class = StateWorkingPieceSerializer
    queryset = StateWorkingPiece.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AssignedOrderView(mixins.ListModelMixin,
                        mixins.CreateModelMixin,
                        generics.GenericAPIView):
    serializer_class = AssignedOrderSerializer
    queryset = AssignedOrder.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class WorkingPlanView(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      generics.GenericAPIView):
    serializer_class = WorkingPlanSerializer
    queryset = WorkingPlan.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class WorkingStepView(mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      generics.GenericAPIView):
    serializer_class = WorkingStepSerializer
    queryset = WorkingStep.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ErrorView(mixins.ListModelMixin,
                mixins.CreateModelMixin,
                generics.GenericAPIView):
    serializer_class = ErrorSerializer
    queryset = Error.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class SettingView(mixins.ListModelMixin,
                  mixins.CreateModelMixin,
                  generics.GenericAPIView):
    serializer_class = SettingSerializer
    queryset = Setting.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class CostumerView(mixins.ListModelMixin,
                   mixins.CreateModelMixin,
                   generics.GenericAPIView):
    serializer_class = CostumerSerializer
    queryset = Costumer.objects.all()

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
