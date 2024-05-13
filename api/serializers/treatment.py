from rest_framework.serializers import ModelSerializer
from infra.models import *


class TreatmentIPCReceivedSerializer(ModelSerializer):
    class Meta:
        model = SessionTreatmentIPCReceived
        fields = "__all__"
