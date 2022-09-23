from django.db import models
import uuid


class PersonalCharacteristics(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    birth_year = models.IntegerField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)
    gender = models.CharField(max_length=256, null=True, blank=True)
    ethnicity = models.CharField(max_length=256, null=True, blank=True)
    body_type = models.CharField(max_length=256, null=True, blank=True)


class PhysicalActivityLevel(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    activity_level_before_pain = models.CharField(max_length=256, null=True, blank=True)
    activity_level_during_pain = models.CharField(max_length=256, null=True, blank=True)
    regular_activity = models.CharField(max_length=256, null=True, blank=True)
    activity_per_week = models.IntegerField(null=True, blank=True)


class BackPainLevel(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    back_pain_level = models.IntegerField(null=True, blank=True)
    is_job_heavy = models.BooleanField(null=True, blank=True)
    is_desk_work_all_day = models.BooleanField(null=True, blank=True)
    healthcare_consult = models.BooleanField(null=True, blank=True)
    pain_relief = models.CharField(max_length=256, null=True, blank=True)
    is_taking_medication = models.BooleanField(null=True, blank=True)


class Diseases(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
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
    pain_since = models.CharField(max_length=256, null=True, blank=True)
    pain_location = models.CharField(max_length=256, null=True, blank=True)
    constant_pain = models.CharField(max_length=256, null=True, blank=True)
    pain_start = models.CharField(max_length=256, null=True, blank=True)
    relation_physical_activity = models.CharField(max_length=256, null=True, blank=True)
    relation_rest = models.CharField(max_length=256, null=True, blank=True)
    is_pain_spreading = models.CharField(max_length=256, null=True, blank=True)
    pain_description = models.CharField(max_length=256, null=True, blank=True)
