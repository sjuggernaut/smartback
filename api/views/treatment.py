import logging
from django.db.utils import IntegrityError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, generics
from infra.domain.alert.generic_sensor_alert import TreatmentAbruptDataSendAlert
from infra.domain.commands import Commands
from api.views.view_config import *

logger = logging.getLogger(__name__)


class TreatmentAbruptEndView(generics.CreateAPIView):
    """
    This is to trigger an abrupt end to the treatment session.
    Send to kafka backend to end the session
    """
    permission_classes = (IsAuthenticated,)
    queryset = None
    serializer_class = None
    pagination_class = None

    def create(self, request, *args, **kwargs):
        try:
            request.data["user"] = request.user.id
            alert = TreatmentAbruptDataSendAlert(command=Commands.treatment_abrupt_end.name, user=request.user.id)
            kafka_service.send(alert)
            return Response(status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class TreatmentOneMinuteEndView(generics.CreateAPIView):
    """
    This is to trigger an end to the One minute treatment cycle (aka Segment).
    Send to kafka backend to end the one minute cycle
    """
    permission_classes = (IsAuthenticated,)
    queryset = None
    serializer_class = None
    pagination_class = None

    def create(self, request, *args, **kwargs):
        try:
            request.data["user"] = request.user.id
            alert = TreatmentAbruptDataSendAlert(command=Commands.treatment_one_min_end.name, user=request.user.id)
            kafka_service.send(alert)
            return Response(status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class TreatmentStartDataSendOneMinuteView(generics.CreateAPIView):
    """
    Start data send for the one minute cycle.
    """
    permission_classes = (IsAuthenticated,)
    queryset = None
    serializer_class = None
    pagination_class = None

    def create(self, request, *args, **kwargs):
        try:
            request.data["user"] = request.user.id
            alert = TreatmentAbruptDataSendAlert(command=Commands.treatment_start_data_send.name, user=request.user.id)
            kafka_service.send(alert)
            return Response(status=status.HTTP_201_CREATED)
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST)
