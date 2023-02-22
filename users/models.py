from django.db import models
import uuid
from django.contrib.auth import get_user_model

DEVICE_TYPE_CHOICES = (
    ("device_semg", "SEMG"),
    ("device_inertial", "INERTIAL"),
    ("device_ir", "IR"),
)


class Devices(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    type = models.CharField(choices=DEVICE_TYPE_CHOICES, default=None, max_length=256)

    class Meta:
        unique_together = (('user', 'type'),)

    def __str__(self):
        return f"[{self.user.username}] <=> [{self.type}]"


class PersonalCharacteristics(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, unique=True, related_name="user_pc")
    birth_year = models.IntegerField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)  # in cms
    weight = models.FloatField(null=True, blank=True)  # In kgs
    gender = models.CharField(max_length=256, null=True, blank=True)
    ethnicity = models.CharField(max_length=256, null=True, blank=True)
    body_type = models.CharField(max_length=256, null=True, blank=True)

    def height_to_meters(self):
        return self.height / 100

    @property
    def get_bmi(self):
        height_mts = self.height_to_meters()
        return self.weight / (height_mts * height_mts)

    class Meta:
        verbose_name = "Personal Characteristics"
        verbose_name_plural = "Personal Characteristics"

    def __str__(self):
        return self.user.username.capitalize()


class PhysicalActivityLevel(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, unique=True)
    activity_level_before_pain = models.CharField(max_length=256, null=True, blank=True)
    activity_level_during_pain = models.CharField(max_length=256, null=True, blank=True)
    regular_activity = models.CharField(max_length=256, null=True, blank=True)
    activity_per_week = models.IntegerField(null=True, blank=True)


class BackPainLevel(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, unique=True)
    back_pain_level = models.IntegerField(null=True, blank=True)
    is_job_heavy = models.BooleanField(null=True, blank=True)
    is_desk_work_all_day = models.BooleanField(null=True, blank=True)
    healthcare_consult = models.BooleanField(null=True, blank=True)
    pain_relief = models.CharField(max_length=256, null=True, blank=True)
    is_taking_medication = models.BooleanField(null=True, blank=True)


class Diseases(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, unique=True)
    chronic_back_pain = models.BooleanField(null=True, blank=True)
    unsteady_gait = models.BooleanField(null=True, blank=True)
    bowel_bladder_symptoms = models.BooleanField(null=True, blank=True)
    relief_with_rest = models.BooleanField(null=True, blank=True)
    leg_pain = models.BooleanField(null=True, blank=True)
    leukaemia = models.BooleanField(null=True, blank=True)
    chemotherapy = models.BooleanField(null=True, blank=True)
    gastrointestinal_carcinoma = models.BooleanField(null=True, blank=True)
    surgery = models.BooleanField(null=True, blank=True)
    myositis = models.BooleanField(null=True, blank=True)


class DecisionLevel2(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, unique=True)
    pain_since = models.CharField(max_length=256, null=True, blank=True)
    pain_location = models.CharField(max_length=256, null=True, blank=True)
    constant_pain = models.CharField(max_length=256, null=True, blank=True)
    pain_start = models.CharField(max_length=256, null=True, blank=True)
    relation_physical_activity = models.CharField(max_length=256, null=True, blank=True)
    relation_rest = models.CharField(max_length=256, null=True, blank=True)
    is_pain_spreading = models.CharField(max_length=256, null=True, blank=True)
    pain_description = models.CharField(max_length=256, null=True, blank=True)
