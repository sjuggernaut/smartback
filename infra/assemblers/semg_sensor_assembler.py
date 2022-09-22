import json

from infra.assemblers.kafka_assembler import KafkaAssembler
from infra.domain.alert.alert import Alert
from kafka.consumer.fetcher import ConsumerRecord


class KafkaSEMGSensorAssembler(KafkaAssembler):
    """
    This assembler is only for the SEMG Sensor Data kafka messages.
    :return Alert
    """

    def assemble(self, kafka_message: ConsumerRecord, meta) -> Alert:
        pass
