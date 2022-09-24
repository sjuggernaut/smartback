from django.db import models
import uuid


class GoldStandardInertialSensors(models.Model):
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


class GoldStandardSEMGSensors(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    rightc4_paraspinal = models.FloatField(null=True, blank=True)  # Not used in the comparison process
    leftc4_paraspinal = models.FloatField(null=True, blank=True)  # Not used in the comparison process
    right_multifidus = models.FloatField(null=True, blank=True)  # Used in the comparison process
    left_multifidus = models.FloatField(null=True, blank=True)  # used in the comparison process
