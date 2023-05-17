import json
import logging
from kafka.consumer.fetcher import ConsumerRecord

from infra.assemblers.kafka_assembler import KafkaAssembler
from infra.domain.alert.alert import Alert
from infra.serializers import *
from infra.exceptions.filter_out import FilterOutException
from infra.models import SessionTypes
from infra.utils import dict_contains_keys, SEMG_DATA_FIELDS

logger = logging.getLogger(__name__)


class KafkaSEMGSensorAssembler(KafkaAssembler):
    """
    This assembler is only for the SEMG Sensor Data kafka messages.
    :return Alert
    """

    def assemble(self, kafka_message: ConsumerRecord) -> Alert:
        logger.info(
            f"SEMGSensor Assembler: Message received from Offset: [{kafka_message.offset}] on topic: [{kafka_message.topic}] at timestamp: [{kafka_message.timestamp}]")
        try:
            original = kafka_message.value.decode("utf-8")
            event = json.loads(original)
            data = event.get("data")
            event_type = event.get("type", None)

            if not dict_contains_keys(data, SEMG_DATA_FIELDS):
                raise FilterOutException(__name__, "SEMG data does not contain all the required fields.")

            data["session"] = event["session"]

            # Prepare serializer data based on type of session
            if event_type and event_type.upper() == SessionTypes.CALIBRATION:
                data["step"] = event["step"]
                serializer = CalibrationStepSEMGDataSerializer(data=data)
            else:
                serializer = SEMGSensorDataSerializer(data=data)

            serializer.is_valid(raise_exception=True)
            serializer.save()
            logger.info(f"SEMGSensor Assembler: [{event.get('type')}] message has been saved. ")
        except Exception as e:
            raise FilterOutException(__name__, e)
