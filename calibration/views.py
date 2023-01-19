import logging
import os

from django.db.utils import IntegrityError

from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from calibration.serializers import *
from infra.producer import Producer
from infra.domain.commands import Commands
from infra.assemblers.device_types import DeviceTypes
from infra.assemblers.command_assemblers.command_assembler import CalibrationCommandAssembler
from infra.service.kafka_service import KafkaService
from smartback.configuration import get_config

from users.models import Devices

logger = logging.getLogger(__name__)

environment = os.getenv("ENVIRONMENT")
configuration = get_config(environment)

# ipc_kafka_service = KafkaService(producer=Producer(configuration.get_kafka_producer_configuration(),
#                                                    configuration.get_kafka_ipc_topic()))
command_assembler = CalibrationCommandAssembler()


class CalibrationSessionCreateView(generics.CreateAPIView):
    """
    Create a new Calibration session for the token user.
    """
    permission_classes = (IsAuthenticated,)
    queryset = Calibration.objects.all()
    serializer_class = CalibrationCreateSerializer
    pagination_class = None

    def create(self, request, *args, **kwargs):
        pass
        # try:
        #     request.data["user"] = request.user.id
        #     serializer = self.get_serializer(data=request.data)
        #     serializer.is_valid(raise_exception=True)
        #     self.perform_create(serializer)
        #     headers = self.get_success_headers(serializer.data)
        #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        # except IntegrityError:
        #     return Response(status=status.HTTP_400_BAD_REQUEST)


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
        pass
        # try:
        #     request.data["user"] = request.user.id
        #     serializer = self.get_serializer(data=request.data)
        #     serializer.is_valid(raise_exception=True)
        #     # self.perform_create(serializer)
        #     headers = self.get_success_headers(serializer.data)
        #
        #     """
        #     KAFKA produce to IPC topic to capture data for the step
        #     Send Calibration ID, Device ID, Step ID,
        #     If the Device ID matches with the consuming process's env var - DEVICE_ID - the sensor will start producing
        #     to the topic.
        #     the produced data includes Calibration ID, Device ID, Step ID
        #     """
        #     self._send_to_kafka(request)
        #
        #     return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        # except IntegrityError as exception:
        #     logger.exception(f"There is an error while adding a calibration step. [{exception}]")
        #     return Response({"message": "Duplicate calibration step failed to add."},
        #                     status=status.HTTP_400_BAD_REQUEST)

    # def _send_to_kafka(self, request):
    #     users_devices = Devices.objects.filter(user=request.user,
    #                                            type__in=[
    #                                                DeviceTypes.device_semg,
    #                                                DeviceTypes.device_inertial,
    #                                                DeviceTypes.device_ir
    #                                            ])
    #     user_semg_device = users_devices.get(type=DeviceTypes.device_semg)
    #     semg_alert = command_assembler.assemble(request, user_semg_device, Commands.calibration_step_start)
    #
    #     user_inertial_device = users_devices.get(type=DeviceTypes.device_inertial)
    #     inertial_alert = command_assembler.assemble(request, user_inertial_device, Commands.calibration_step_start)
    #
    #     user_ir_device = users_devices.get(type=DeviceTypes.device_ir)
    #     ir_alert = command_assembler.assemble(request, user_ir_device, Commands.calibration_step_start)
    #
    #     ipc_kafka_service.send(semg_alert)
    #     ipc_kafka_service.send(inertial_alert)
    #     ipc_kafka_service.send(ir_alert)
