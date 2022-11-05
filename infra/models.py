from django.db import models
import uuid
from django.contrib.auth import get_user_model

from users.models import Devices

STATUS_CHOICES = (
    ("CREATED", "Created"),
    ("COMPLETED", "Completed"),
    ("STARTED", "Started"),
    ("FAILED", "Failed"),
)


class Session(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0], max_length=256)
    type = models.CharField(max_length=256)  # SessionType


class IRSensorData(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        verbose_name="Session"
    )
    device = models.ForeignKey(Devices, on_delete=models.PROTECT)
    thermal = models.FloatField(null=True, blank=True)


class InertialSensorData(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        verbose_name="Session"
    )
    device = models.ForeignKey(Devices, on_delete=models.PROTECT)

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


class SEMGSensorData(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        verbose_name="Session"
    )
    device = models.ForeignKey(Devices, on_delete=models.PROTECT)
    rightc4_paraspinal = models.FloatField(null=True, blank=True)
    leftc4_paraspinal = models.FloatField(null=True, blank=True)
    right_multifidus = models.FloatField(null=True, blank=True)
    left_multifidus = models.FloatField(null=True, blank=True)


class Procedure(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256)

    def __str__(self):
        return self.name


class ProcedureStep(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=256)
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name='procedure_steps')

    def __str__(self):
        return f"{self.procedure} :: {self.name}"


class ProcedureStepOrder(models.Model):
    step = models.ForeignKey(ProcedureStep, on_delete=models.CASCADE)
    order = models.IntegerField(max_length=2)


class CalibrationStep(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, default=None)
    step = models.ForeignKey(ProcedureStep, on_delete=models.CASCADE, default=None)
    started_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['session', 'step'], name='Single-Calibration-with-a-step-constraint')
        ]

class SessionTreatmentIPCReceived(models.Model):
    """
    This model records the time and status of the DE receiving one mind end commands for treatment session from sensors
    Identify the multiple records per session by the processing_status
    """
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, default=None)
    semg_received = models.BooleanField()
    semg_received_time = models.DateTimeField(auto_now_add=True)
    inertial_received = models.BooleanField()
    inertial_received_time = models.DateTimeField(auto_now_add=True)
    ir_received = models.BooleanField()
    ir_received_time = models.DateTimeField(auto_now_add=True)
    processing_status = models.BooleanField(default=False)