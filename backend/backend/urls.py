
from django import urls
from django.contrib import admin
from django.urls import path, include
from mesapi.views import *


urlpatterns = [
    # url for API authenication
    path('api-auth/', include('rest_framework.urls')),
    path('admin/', admin.site.urls),
    path('/api/Costumer', CostumerView.as_view()),
    path('/api/Setting', SettingView.as_view()),
    path('/api/Error', ErrorView.as_view()),
    path('/api/WorkingStep', WorkingStepView.as_view()),
    path('/api/WorkingPlan', WorkingPlanView.as_view()),
    path('/api/AssignedOrder', AssignedOrderView.as_view()),
    path('/api/StateWorkingPiece', StateWorkingPieceView.as_view()),
    path('/api/VisualisationTask', VisualisationTaskView.as_view()),
    path('/api/StateVisualisationUnit', StateVisualisationUnitView.as_view()),
    path('/api/StatePLC', StatePLCView.as_view()),
    path('api/', APIOverview.as_view()),
]
