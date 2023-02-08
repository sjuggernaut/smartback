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

SESSION_TYPES = (
    ("CALIBRATION", "Calibration"),
    ("TREATMENT", "Treatment"),
)

"""
========================================================================================================
Session Data Models 
========================================================================================================
"""


class SessionTypes(models.TextChoices):
    CALIBRATION = "CALIBRATION", "Calibration"
    TREATMENT = "TREATMENT", "Treatment"


class StatusChoices(models.TextChoices):
    CREATED = "CREATED", "Created"
    COMPLETED = "COMPLETED", "Completed"
    STARTED = "STARTED", "Started"
    FAILED = "FAILED", "Failed"


class Session(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=StatusChoices.choices, default=StatusChoices.CREATED, max_length=256)
    type = models.CharField(choices=SessionTypes.choices, default=SessionTypes.CALIBRATION,
                            max_length=256)  # SessionType


"""
========================================================================================================
Generic Sensor Data Models 
========================================================================================================
"""


class GenericInertialSensorsData(models.Model):
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

    com_posx = models.FloatField(null=True, blank=True)
    com_posy = models.FloatField(null=True, blank=True)
    com_posz = models.FloatField(null=True, blank=True)

    class Meta:
        abstract = True


class GenericSEMGSensorsData(models.Model):
    rightc4_paraspinal = models.FloatField(null=True, blank=True)
    leftc4_paraspinal = models.FloatField(null=True, blank=True)
    right_multifidus = models.FloatField(null=True, blank=True)
    left_multifidus = models.FloatField(null=True, blank=True)

    class Meta:
        abstract = True


class GenericIRSensorData(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        verbose_name="Session"
    )
    thermal = models.FloatField(null=True, blank=True)
    read_status = models.BooleanField(default=False)

    class Meta:
        abstract = True

"""
========================================================================================================
Calibration Data Models 
========================================================================================================
"""


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
    read_status = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['session', 'step'], name='Single-Calibration-with-a-step-constraint')
        ]


class CalibrationStepSEMGData(GenericSEMGSensorsData):
    data_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        verbose_name="Session"
    )
    read_status = models.BooleanField(default=False)
    step = models.ForeignKey(CalibrationStep, on_delete=models.CASCADE, default=None)


class CalibrationStepInertialData(GenericInertialSensorsData):
    data_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        verbose_name="Session"
    )
    read_status = models.BooleanField(default=False)
    step = models.ForeignKey(CalibrationStep, on_delete=models.CASCADE, default=None)


class CalibrationStepIRData(GenericIRSensorData):
    step = models.ForeignKey(CalibrationStep, on_delete=models.CASCADE, default=None)


class ProcedureGoldStandardInertialData(GenericInertialSensorsData):
    """
    Model class for Calibration Gold Standard for a given procedure. Calibration process can have multiple procedures.

    Usage Phase: Calibration
    """
    data_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, default=None)
    is_final_data = models.BooleanField(default=False)


class ProcedureGoldStandardSEMGData(GenericSEMGSensorsData):
    """
    Model class for Calibration Gold Standard for a given procedure. Calibration process can have multiple procedures.

    Usage Phase: Calibration
    """
    data_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, default=None)
    is_final_data = models.BooleanField(default=False)


"""
========================================================================================================
Treatment Data Models 
========================================================================================================
"""


class UserGoldStandardInertialData(GenericInertialSensorsData):
    """
    Model class for User's gold standard data - used during Treatment phase for the user. The values are created and stored to this model at the end of calibration phase.

    Usage Phase: Treatment
    """
    data_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    is_final_data = models.BooleanField(default=False)


class UserGoldStandardSEMGData(GenericSEMGSensorsData):
    """
    Model class for User's gold standard data - used during Treatment phase for the user. The values are created and stored to this model at the end of calibration phase.

    Usage Phase: Treatment
    """
    data_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    is_final_data = models.BooleanField(default=False)


class TreatmentGoldStandardInertialData(GenericInertialSensorsData):
    """
    This model is for configuration data of treatment gold standard

    Model class for Treatment Gold standard - only one row data possible in this model at any point in time.
    Usage Phase: Treatment
    """
    data_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    is_final_data = models.BooleanField(default=False)


class TreatmentGoldStandardSEMGData(GenericSEMGSensorsData):
    """
    This model is for configuration data of treatment gold standard

    Model class for Treatment Gold standard - only one row data possible in this model at any point in time.
    Usage Phase: Treatment
    """
    data_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    is_final_data = models.BooleanField(default=False)


class SessionTreatmentIPCReceived(models.Model):
    """
    This model records the time and status of the engine receiving one min end commands for treatment session from sensors
    Identify the multiple records per session by the processing_status

    This record for a session is created when a new treatment session record is created.

    Usage Phase: Treatment
    """
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, default=None)
    processing_status = models.BooleanField(default=False)  # Once the loop cycle finishes, set this to True

    # SEMG Received data
    semg_received = models.BooleanField()
    semg_received_time = models.DateTimeField(auto_now_add=True)

    # Inertial Received data
    inertial_received = models.BooleanField()
    inertial_received_time = models.DateTimeField(auto_now_add=True)

    # IR Received data
    ir_received = models.BooleanField()
    ir_received_time = models.DateTimeField(auto_now_add=True)


class TreatmentSEMGData(GenericSEMGSensorsData):
    data_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        verbose_name="Session"
    )
    read_status = models.BooleanField(default=False)


class TreatmentInertialData(GenericInertialSensorsData):
    data_id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        verbose_name="Session"
    )
    read_status = models.BooleanField(default=False)
