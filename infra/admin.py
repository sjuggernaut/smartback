from django.contrib import admin
from infra.models import SessionTreatmentIPCReceived, IRSensorData, SEMGSensorData, InertialSensorData, Session, CalibrationStep, ProcedureStep, Procedure

admin.site.register(SessionTreatmentIPCReceived)
admin.site.register(InertialSensorData)
admin.site.register(SEMGSensorData)
admin.site.register(IRSensorData)
admin.site.register(Session)
admin.site.register(CalibrationStep)
admin.site.register(ProcedureStep)
admin.site.register(Procedure)
