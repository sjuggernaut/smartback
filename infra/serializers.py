from rest_framework.serializers import ModelSerializer
from infra.models import SEMGSensorData, InertialSensorData, IRSensorData, Session, CalibrationStep, \
    CalibrationStepSEMGData, CalibrationStepInertialData, CalibrationStepIRData


class SEMGSensorDataSerializer(ModelSerializer):
    class Meta:
        model = SEMGSensorData
        fields = '__all__'


class CalibrationStepSEMGDataSerializer(ModelSerializer):
    class Meta:
        model = CalibrationStepSEMGData
        fields = '__all__'


class InertialSensorDataSerializer(ModelSerializer):
    class Meta:
        model = InertialSensorData
        fields = '__all__'


class CalibrationStepInertialDataSerializer(ModelSerializer):
    class Meta:
        model = CalibrationStepInertialData
        fields = '__all__'


class IRSensorDataSerializer(ModelSerializer):
    class Meta:
        model = IRSensorData
        fields = '__all__'


class CalibrationStepIRDataSerializer(ModelSerializer):
    class Meta:
        model = CalibrationStepIRData
        fields = '__all__'


class SessionCreateSerializer(ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'


class CalibrationStepCreateSerializer(ModelSerializer):
    class Meta:
        model = CalibrationStep
        fields = '__all__'
