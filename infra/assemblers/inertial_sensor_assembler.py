import json
import logging

from infra.assemblers.kafka_assembler import KafkaAssembler
from infra.domain.alert.alert import Alert
from kafka.consumer.fetcher import ConsumerRecord
from infra.serializers import InertialSensorDataSerializer, CalibrationStepInertialDataSerializer
from infra.exceptions.filter_out import FilterOutException
from infra.models import SessionTypes

logger = logging.getLogger(__name__)


class KafkaInertialSensorAssembler(KafkaAssembler):
    """
    This assembler is only for the Inertial Sensor Data kafka messages.
    :return Alert
    """

    def assemble(self, kafka_message: ConsumerRecord) -> Alert:
        logger.info(
            f"InertialSensor Assembler: Message received from [{kafka_message.offset}] on topic [{kafka_message.topic}] at [{kafka_message.timestamp}]")

        try:
            original = kafka_message.value.decode("utf-8")
            event = json.loads(original)
            data = event.get("data")
            event_type = event.get("type", None)

            if event_type and event_type == SessionTypes.CALIBRATION:
                serializer = CalibrationStepInertialDataSerializer(data=data)
            else:
                serializer = InertialSensorDataSerializer(data=data)

            serializer.is_valid(raise_exception=True)
            serializer.save()

            logger.info(f"InertialSensor Assembler: [{event.get('type')}] message has been saved. ")
        except Exception as e:
            raise FilterOutException(__name__, e)
