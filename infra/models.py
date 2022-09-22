from django.db import models
import uuid


class Session(models.Model):
    pass


class IRSensorData(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        verbose_name="Session"
    )


class InertialSensorData(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        verbose_name="Session"
    )
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
    rightc4_paraspinal = models.FloatField(null=True, blank=True)
    leftc4_paraspinal = models.FloatField(null=True, blank=True)
    right_multifidus = models.FloatField(null=True, blank=True)
    left_multifidus = models.FloatField(null=True, blank=True)
