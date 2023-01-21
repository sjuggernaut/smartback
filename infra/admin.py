from django.contrib import admin
from infra.models import *

admin.site.register(SessionTreatmentIPCReceived)

admin.site.register(CalibrationStepSEMGData)
admin.site.register(CalibrationStepInertialData)

admin.site.register(TreatmentGoldStandardInertialData)
admin.site.register(TreatmentGoldStandardSEMGData)

admin.site.register(UserGoldStandardInertialData)
admin.site.register(UserGoldStandardSEMGData)

admin.site.register(Session)
admin.site.register(CalibrationStep)
admin.site.register(ProcedureStep)
admin.site.register(Procedure)
