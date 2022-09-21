import json

from infra.assemblers.kafka_assembler import KafkaAssembler
from infra.domain.alert.alert import Alert


class KafkaInertialSensorAssembler(KafkaAssembler):
    """
    This assembler is only for the Inertial Sensor Data kafka messages.
    :return Alert
    """

    def assemble(self, kafka_alert, meta) -> Alert:
        pass
