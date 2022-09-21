import json

from infra.assemblers.kafka_assembler import KafkaAssembler
from infra.domain.alert.alert import Alert



class KafkaSEMGSensorAssembler(KafkaAssembler):
    """
    This assembler is only for the SEMG Sensor Data kafka messages.
    :return Alert
    """

    def assemble(self, kafka_alert, meta) -> Alert:
        pass

