import logging

from kafka.consumer.fetcher import ConsumerRecord
from infra.assemblers.kafka_assembler import KafkaAssembler

logger = logging.getLogger(__name__)


# Each Topic consumer will call this accept_record method to process it's message
class KafkaAlertApi:
    def __init__(self, alert_assembler: KafkaAssembler):
        self._alert_assembler = alert_assembler

    def accept_record(self, kafka_consumer_record: ConsumerRecord):
        try:
            logger.info(f"Processing ConsumerRecord from offset: [{kafka_consumer_record.offset}]")
            alert = self._alert_assembler.assemble(kafka_consumer_record)
        except Exception as exception:
            logger.exception(f"The kafka event could not be assembled {exception}")

        # Get the alert and store to Redis - all processed and unprocessed alerts are in redis.
