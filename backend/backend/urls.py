from mesbackend.plcserviceordersocket import PLCServiceOrderSocket
from mesbackend.plcstatesocket import PLCStateSocket
from multiprocessing import Process
import django
from django import urls
from django.contrib import admin
from django.urls import path, include
from mesapi.views import *


urlpatterns = [
    # url for API authenication
    path("api-auth/", include("rest_framework.urls")),
    # API urls. Each model has a endpoint for a view for all entities
    # and a enpoint for a single entity of an object
    path("api/Costumer/byName/<str:firstName>/<str:lastName>", SingleCostumerByNameView.as_view()),
    path("api/Costumer/<pk>", SingleCostumerView.as_view()),
    path("api/Costumer/", CostumerView.as_view()),
    path("api/Setting/<pk>", SingleSettingView.as_view()),
    path("api/Setting/", SettingView.as_view()),
    path("api/Error/<pk>", SingleErrorView.as_view()),
    path("api/Error/", ErrorView.as_view()),
    path("api/WorkingStep/<pk>", SingleWorkingStepView.as_view()),
    path("api/WorkingStep/", WorkingStepView.as_view()),
    path("api/WorkingPlan/<pk>", SingleWorkingPlanView.as_view()),
    path("api/WorkingPlan/", WorkingPlanView.as_view()),
    path("api/AssignedOrder/<pk>", SingleAssignedOrderView.as_view()),
    path("api/AssignedOrder/", AssignedOrderView.as_view()),
    path("api/StateWorkingPiece/<pk>", SingleStateWorkingPieceView.as_view()),
    path("api/StateWorkingPiece/", StateWorkingPieceView.as_view()),
    path("api/StateVisualisationUnit/<pk>",
         SingleStateVisualisationUnitView.as_view()),
    path("api/StateVisualisationUnit/", StateVisualisationUnitView.as_view()),
    path("api/StatePLC/<pk>", SingleStatePLCView.as_view()),
    path("api/StatePLC/", StatePLCView.as_view()),
    path("api/Buffer/<pk>", SingleBuffer.as_view()),
    path("api/Buffer/", BufferView.as_view()),
    # Overview for all endpoints
    path("api/", APIOverview.as_view()),
    # admin panel as landing page
    path("", admin.site.urls),
]

try:
    serviceProcess = Process(target=PLCServiceOrderSocket().runServer)
    stateProcess = Process(target=PLCStateSocket().runServer)
    # start processes
    print("Starting sockets")
    serviceProcess.start()
    stateProcess.start()
except Exception as e:
    print(e)
