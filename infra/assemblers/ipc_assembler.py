import json
import logging

from infra.assemblers.kafka_assembler import KafkaAssembler
from infra.domain.alert.alert import Alert
from kafka.consumer.fetcher import ConsumerRecord

logger = logging.getLogger(__name__)

_COMMAND_FROM_BACKEND = "from_backend"


def assemble_ipc_payload(payload_data: dict, command: str) -> str:
    pass
