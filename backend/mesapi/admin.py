"""
Filename: admin.py
Version name: 0.1, 2021-05-14
Short description: All models get registered here for the admin panel so they can be managed from it

(C) 2003-2021 IAS, Universitaet Stuttgart

"""


from django.contrib import admin

from .models import *

# Register all the models from models.py
admin.site.register(StateWorkingPiece)
admin.site.register(StatePLC)
admin.site.register(StateVisualisationUnit)
admin.site.register(AssignedOrder)
admin.site.register(WorkingPlan)
admin.site.register(WorkingStep)
admin.site.register(VisualisationTask)
admin.site.register(Error)
admin.site.register(Setting)
