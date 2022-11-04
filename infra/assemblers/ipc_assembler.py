import json
import logging

from kafka.consumer.fetcher import ConsumerRecord
from infra.exceptions.filter_out import FilterOutException
from infra.exceptions.invalid_command import InvalidCommandException
from infra.domain.commands import Commands

logger = logging.getLogger(__name__)

_COMMAND_FROM_BACKEND = "from_backend"


class IPCCommandAssembler:
    """
    Assemble IPC commands from sensors.
    """

    def assemble(self, kafka_message: ConsumerRecord):
        logger.info(
            f"IPCAssembler: Message received from [{kafka_message.offset}] on topic [{kafka_message.topic}] at [{kafka_message.timestamp}]")

        try:
            original = kafka_message.value.decode("utf-8")
            event = json.loads(original)

            command_text = event.get("command")
            command = Commands.__getitem__(command_text)
            self.get_assembler(command).assemble(event)
        except KeyError:
            raise InvalidCommandException(command_text)
        except Exception as e:
            raise FilterOutException(__name__, e)

    def get_assembler(self, command: Commands):
        return command.assembler
