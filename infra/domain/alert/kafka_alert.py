import logging

from kafka.consumer.fetcher import ConsumerRecord
from infra.assemblers.kafka_assembler import KafkaAssembler
from infra.exceptions.filter_out import FilterOutException

logger = logging.getLogger(__name__)


class KafkaAlertApi:
    def __init__(self, alert_assembler: KafkaAssembler):
        self._alert_assembler = alert_assembler

    def accept_record(self, kafka_consumer_record: ConsumerRecord):
        try:
            logger.info(f"Processing ConsumerRecord from offset: [{kafka_consumer_record.offset}]")
            alert = self._alert_assembler.assemble(kafka_consumer_record)
        except FilterOutException:
            logger.exception(f"The kafka event is filtered out.")
        except Exception as exception:
            logger.exception(f"The kafka event could not be assembled {exception}")
