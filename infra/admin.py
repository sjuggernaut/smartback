from django.contrib import admin
from infra.models import *

admin.site.register(SessionTreatmentIPCReceived)
admin.site.register(GenericSEMGSensorsData)
admin.site.register(GenericInertialSensorsData)
admin.site.register(IRSensorData)
admin.site.register(Session)
admin.site.register(CalibrationStep)
admin.site.register(ProcedureStep)
admin.site.register(Procedure)
