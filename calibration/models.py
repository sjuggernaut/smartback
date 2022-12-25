from django.db import models
import uuid
from django.contrib.auth import get_user_model

STATUS_CHOICES = (
    ("CREATED", "Created"),
    ("COMPLETED", "Completed"),
    ("STARTED", "Started"),
    ("FAILED", "Failed"),
)





# class Procedure(models.Model):
#     id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=256)
#
#     def __str__(self):
#         return self.name
#
#
# class ProcedureStep(models.Model):
#     id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
#     name = models.CharField(max_length=256)
#     procedure = models.ForeignKey(Procedure, on_delete=models.CASCADE, related_name='procedure_steps')
#
#     def __str__(self):
#         return f"{self.procedure} :: {self.name}"
#
#
# class ProcedureStepOrder(models.Model):
#     step = models.ForeignKey(ProcedureStep, on_delete=models.CASCADE)
#     order = models.IntegerField(max_length=2)


# class GoldStandardInertialSensors(GenericInertialSensors):
#     step = models.ForeignKey(ProcedureStep, on_delete=models.CASCADE, default=None)
#
#
# class GoldStandardSEMGSensors(GenericSEMGSensors):
#     step = models.ForeignKey(ProcedureStep, on_delete=models.CASCADE, default=None)


class Calibration(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    started_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=STATUS_CHOICES, default=STATUS_CHOICES[0][0], max_length=256)

    def __str__(self):
        return f"{self.user.username}::{self.id}"
#
#
# class CalibrationStep(models.Model):
#     id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
#     session = models.ForeignKey(Calibration, on_delete=models.CASCADE, default=None)
#     step = models.ForeignKey(ProcedureStep, on_delete=models.CASCADE, default=None)
#     started_at = models.DateTimeField(auto_now_add=True)
#
#     class Meta:
#         constraints = [
#             models.UniqueConstraint(fields=['session', 'step'], name='Single-Calibration-with-a-step-constraint')
#         ]


