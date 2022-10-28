from django.db import models
import uuid

from infra.models import Session
from calibration.models import CalibrationStep

class InertialSensorsData(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    l5s1_lateral = models.FloatField(null=True, blank=True)
    l5s1_axial = models.FloatField(null=True, blank=True)
    l5s1_flexion = models.FloatField(null=True, blank=True)

    l4l3_lateral = models.FloatField(null=True, blank=True)
    l4l3_axial = models.FloatField(null=True, blank=True)
    l4l3_flexion = models.FloatField(null=True, blank=True)

    l1t12_lateral = models.FloatField(null=True, blank=True)
    l1t12_axial = models.FloatField(null=True, blank=True)
    l1t12_flexion = models.FloatField(null=True, blank=True)

    t9t8_lateral = models.FloatField(null=True, blank=True)
    t9t8_axial = models.FloatField(null=True, blank=True)
    t9t8_flexion = models.FloatField(null=True, blank=True)

    t1c7_lateral = models.FloatField(null=True, blank=True)
    t1c7_axial = models.FloatField(null=True, blank=True)
    t1c7_flexion = models.FloatField(null=True, blank=True)

    c1head_lateral = models.FloatField(null=True, blank=True)
    c1head_axial = models.FloatField(null=True, blank=True)
    c1head_flexion = models.FloatField(null=True, blank=True)


class SEMGSensorsData(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    rightc4_paraspinal = models.FloatField(null=True, blank=True)  # Not used in the comparison process
    leftc4_paraspinal = models.FloatField(null=True, blank=True)  # Not used in the comparison process
    right_multifidus = models.FloatField(null=True, blank=True)  # USED in the comparison process
    left_multifidus = models.FloatField(null=True, blank=True)  # USED in the comparison process


class IRensorsData(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    thermal_value = models.FloatField(null=True, blank=True)


class CalibrationData(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    semg = models.ForeignKey(SEMGSensorsData, on_delete=models.CASCADE, related_name='calibration_semg')
    inertial = models.ForeignKey(InertialSensorsData, on_delete=models.CASCADE, related_name='calibration_inertial')
    ir = models.ForeignKey(InertialSensorsData, on_delete=models.CASCADE, related_name='calibration_inertial')
    status = models.CharField(max_length=256)
    step = models.ForeignKey(CalibrationStep, on_delete=models.CASCADE)

class TreatmentData(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    semg = models.ForeignKey(SEMGSensorsData, on_delete=models.CASCADE, related_name='calibration_semg')
    inertial = models.ForeignKey(InertialSensorsData, on_delete=models.CASCADE, related_name='calibration_inertial')
    ir = models.ForeignKey(InertialSensorsData, on_delete=models.CASCADE, related_name='calibration_inertial')
    status = models.CharField(max_length=256)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)

