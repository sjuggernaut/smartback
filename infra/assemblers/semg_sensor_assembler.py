import logging

from infra.assemblers.kafka_assembler import KafkaAssembler
from infra.domain.alert.alert import Alert
from kafka.consumer.fetcher import ConsumerRecord

logger = logging.getLogger(__name__)


class KafkaSEMGSensorAssembler(KafkaAssembler):
    """
    This assembler is only for the SEMG Sensor Data kafka messages.
    :return Alert
    """

    def assemble(self, kafka_message: ConsumerRecord, meta) -> Alert:
        original = kafka_message.value.decode("utf-8")
        logger.info(
            f"SEMG Sensor Assembler: Message received from [{kafka_message.offset}] on topic [{kafka_message.topic}] at [{kafka_message.timestamp}]")
