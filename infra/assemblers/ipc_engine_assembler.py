import json
import logging

from kafka.consumer.fetcher import ConsumerRecord
from infra.exceptions.filter_out import FilterOutException
from infra.exceptions.invalid_command import InvalidCommandException
from infra.domain.commands import Commands

from infra.domain.alert.calibration_alert import CalibrationEndAlert
from infra.domain.sensor_commands import SensorCommands

logger = logging.getLogger(__name__)

_COMMAND_FROM_BACKEND = "from_backend"


class IPCEngineCommandAssembler:
    """
    Assemble IPC commands coming into engine.
    """

    def __init__(self, kafka_service):
        self._kafka_service = kafka_service

    def assemble(self, kafka_message: ConsumerRecord):
        logger.info(
            f"IPCEngineAssembler: Message received from [{kafka_message.offset}] on topic [{kafka_message.topic}] at [{kafka_message.timestamp}]")

        try:
            original = kafka_message.value.decode("utf-8")
            event = json.loads(original)

            command_text = event.get("command")
            command = Commands.__getitem__(command_text)

            if command == Commands.calibration_end:
                calibration_end_alert = CalibrationEndAlert(command=SensorCommands.set_calibration_end.name, session="")
                self._kafka_service.send(calibration_end_alert)

            if command == Commands.treatment_one_min_end:
                session = event.get("session")
                treatment_one_min_end_alert = CalibrationEndAlert(command=SensorCommands.data_send_pause.name,
                                                                  session=session)
                self._kafka_service.send(treatment_one_min_end_alert)

            alert = self.get_assembler(command).assemble(event)
            if alert:
                self._kafka_service.send(alert)
            else:
                logger.exception(f"Alert could not sent to the sensors for the event: {event}")
        except KeyError:
            raise InvalidCommandException(command_text)
        except Exception as e:
            raise FilterOutException(__name__, e)

    def get_assembler(self, command: Commands):
        return command.assembler
