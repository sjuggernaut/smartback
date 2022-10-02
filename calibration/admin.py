from django.contrib import admin
from calibration.models import *

# Register your models here.
admin.site.register(GoldStandardSEMGSensors)
admin.site.register(GoldStandardInertialSensors)
admin.site.register(CalibrationInertialSensors)
admin.site.register(CalibrationSEMGSensors)
admin.site.register(ProcedureStep)
admin.site.register(Procedure)
admin.site.register(ProcedureStepOrder)
admin.site.register(Calibration)