from django.contrib import admin
from calibration.models import GoldStandardInertialSensors, GoldStandardSEMGSensors

# Register your models here.
admin.site.register(GoldStandardSEMGSensors)
admin.site.register(GoldStandardInertialSensors)