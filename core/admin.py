from django.contrib import admin
from .models import (
    CentreDI, GMR, Projet, RoleType, 
    GroupeInterlocuteurs, Interlocuteur,
    ProcessusEtape, Action, Subtask
)

admin.site.register(CentreDI)
admin.site.register(GMR)
admin.site.register(Projet)
admin.site.register(RoleType)
admin.site.register(GroupeInterlocuteurs)
admin.site.register(Interlocuteur)
admin.site.register(ProcessusEtape)
admin.site.register(Action)
admin.site.register(Subtask) 