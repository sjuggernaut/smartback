import logging

from abc import ABC, abstractmethod

from infra.domain.alert.alert import Alert
from kafka.consumer.fetcher import ConsumerRecord

from rest_framework.request import Request
from users.models import Devices
from infra.assemblers.commands import Commands
from infra.domain.alert.calibration_alert import CalibrationAlert

logger = logging.getLogger(__name__)

_COMMAND_FROM_BACKEND = "from_backend"


class CommandAssembler(ABC):
    @abstractmethod
    def assemble(self, request: Request, device: Devices, command: Commands) -> Alert:
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
