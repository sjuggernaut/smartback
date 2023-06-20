from rest_framework.serializers import ModelSerializer

from infra.models import *
from api.serializers.treatment import TreatmentIPCReceivedSerializer


class SessionSerializer(ModelSerializer):
    def to_representation(self, instance):
        response = super().to_representation(instance)
        response['segments'] = []
        return response

    class Meta:
        model = Session
        fields = "__all__"


class SessionDetailSerializer(ModelSerializer):
    def to_representation(self, instance):
        response = super().to_representation(instance)
        session_treatment_ipc = SessionTreatmentIPCReceived.objects.values().filter(session=instance).order_by(
            'created_at', 'processing_status')
        response['segments'] = TreatmentIPCReceivedSerializer(session_treatment_ipc, many=True).data
        return response

    class Meta:
        model = Session
        fields = "__all__"
