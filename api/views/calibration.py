import logging
from django.db.utils import IntegrityError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics

from infra.models import CalibrationStep
from infra.domain.alert.generic_sensor_alert import CalibrationStepStartAlertEngine, CalibrationEndAlertEngine
from infra.domain.commands import Commands
from api.serializers.calibration import CalibrationStepSerializer
from api.views.view_config import *

logger = logging.getLogger(__name__)


class CalibrationStepCreateView(generics.CreateAPIView):
    """
    Create a new step for the authorized user's calibration session
    Send to kafka backend to start the step
    """
    permission_classes = (IsAuthenticated,)
    queryset = CalibrationStep.objects.all()
    serializer_class = CalibrationStepSerializer
    pagination_class = None

    def create(self, request, *args, **kwargs):
        try:
            request.data["user"] = request.user.id
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            step = request.data["step"]
            alert = CalibrationStepStartAlertEngine(command=Commands.calibration_step_start.name,
                                                    user=request.user.id,
                                                    step=step)
            kafka_service.send(alert)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CalibrationEndView(generics.CreateAPIView):
    """
    End the session for the authorized user's calibration
    Send to kafka backend to end the session
    """
    permission_classes = (IsAuthenticated,)
    queryset = CalibrationStep.objects.all()
    serializer_class = CalibrationStepSerializer
    pagination_class = None

    def create(self, request, *args, **kwargs):
        try:
            request.data["user"] = request.user.id
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)

            procedure = request.data["procedure"]
            alert = CalibrationEndAlertEngine(command=Commands.calibration_end.name,
                                              user=request.user.id,
                                              procedure=procedure)
            kafka_service.send(alert)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
