from rest_framework.serializers import ModelSerializer

from infra.models import *


class CalibrationStepSerializer(ModelSerializer):
    class Meta:
        model = CalibrationStep
        fields = "__all__"
