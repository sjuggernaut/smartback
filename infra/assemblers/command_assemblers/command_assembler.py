import logging

from abc import ABC, abstractmethod

from kafka.consumer.fetcher import ConsumerRecord
from infra.domain.command_process import CommandProcess
from rest_framework.request import Request
from infra.models import Devices
from infra.domain.commands import Commands
from infra.domain.alert.alert import Alert
from infra.domain.alert.calibration_alert import CalibrationAlert

logger = logging.getLogger(__name__)

_COMMAND_FROM_BACKEND = "from_backend"


class CommandAssembler(ABC):
    @abstractmethod
    def assemble(self, kafka_message: ConsumerRecord) -> CommandProcess:
        pass


class CalibrationCommandAssembler(CommandAssembler):
    def assemble(self, request: Request, device: Devices, command: Commands) -> Alert:
        session = request.data.get("session")
        step = request.data.get("step")

        return CalibrationAlert(
            device_id=str(device.id),
            command=command.name,
            direction=_COMMAND_FROM_BACKEND,
            session=session,
            step=step
        )
