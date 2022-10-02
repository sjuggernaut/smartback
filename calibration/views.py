from django.shortcuts import render
import logging
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from calibration.models import Calibration
from calibration.serializers import *
from django.db.utils import IntegrityError
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


class CalibrationSessionCreateView(generics.CreateAPIView):
    """
    Create a new Calibration session for the token user.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Calibration.objects.all()
    serializer_class = CalibrationCreateSerializer
    pagination_class = None

    def create(self, request, *args, **kwargs):
        try:
            request.data["user"] = request.user.id
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except IntegrityError:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class CalibrationStepCreateView(generics.CreateAPIView):
    """
    Add a new Calibration Session Step for the user.
    This means the FE will start calibration process for a Procedure Step
    This CalibrationStep instance will be used to identify the data from the 3 Sensors : Inertial, SEMG and IR data.
    """
    permission_classes = (IsAuthenticated,)
    queryset = CalibrationStep.objects.all()
    serializer_class = CalibrationStepCreateSerializer
    pagination_class = None

    def create(self, request, *args, **kwargs):
        try:
            request.data["user"] = request.user.id
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except IntegrityError as exception:
            logger.exception(f"There is an error while adding a calibration step. [{exception}]")
            return Response({"message": "Duplicate calibration step failed to add."}, status=status.HTTP_400_BAD_REQUEST)
