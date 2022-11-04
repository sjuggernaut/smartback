from rest_framework.serializers import ModelSerializer
from infra.models import SEMGSensorData, InertialSensorData, IRSensorData, Session, CalibrationStep


class SEMGSensorDataSerializer(ModelSerializer):
    class Meta:
        model = SEMGSensorData
        fields = '__all__'


class InertialSensorDataSerializer(ModelSerializer):
    class Meta:
        model = InertialSensorData
        fields = '__all__'


class IRSensorDataSerializer(ModelSerializer):
    class Meta:
        model = IRSensorData
        fields = '__all__'


class SessionCreateSerializer(ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'


class CalibrationStepCreateSerializer(ModelSerializer):
    class Meta:
        model = CalibrationStep
        fields = '__all__'
