# When the UI triggers a start process - generate a UNIQUE ID for the user
# send this key always in the KAFKA messages from that user for that session
# the UNIQUE ID can be called SESSION_ID in the kafka message
# SESSION_ID is mapped to a USER in the django db.


# Consumer thread runs continously to read the messages from topic and send to assembler
# From the assembler - return a sensorData POJO class object
#
import logging
import threading
from abc import ABCMeta, abstractmethod

from kafka import KafkaConsumer
from infra.assemblers.error_handler import KafkaErrorHandler

logger = logging.getLogger(__name__)
_KAFKA_MAX_INT_VALUE = 2147483647


class KafkaConsumerConfiguration(metaclass=ABCMeta):
    @abstractmethod
    def get_bootstrap_servers(self):
        pass

    @abstractmethod
    def get_consumer_group_id(self):
        pass

    @abstractmethod
    def get_consumer_timeout_ms(self):
        pass


class Consumer(threading.Thread):
    def __init__(
            self,
            kafka_consumer_configuration: KafkaConsumerConfiguration,
            topic: str,
            error_handler: KafkaErrorHandler,
            callback_function=lambda event: print(event),
            **kwargs
    ):
        threading.Thread.__init__(self, name=f"kafkaconsumer_[{topic}]")
        self._stop_event = threading.Event()
        self._boostrap_servers = kafka_consumer_configuration.get_bootstrap_servers()
        self._topic = topic
        self._group_id = kafka_consumer_configuration.get_consumer_group_id()
        self._consumer_timeout_ms = kafka_consumer_configuration.get_consumer_timeout_ms()
        self._error_handler = error_handler
        self._callback_function = callback_function
        if kwargs:
            self._kwargs = kwargs

    def stop(self):
        self._stop_event.set()

    def run(self):
        consumer = KafkaConsumer(
            boostrap_servers=self._boostrap_servers,
            auto_offset_reset="earliest",
            group_id=self._group_id,
            consumer_timeout_ms=self._consumer_timeout_ms,
            max_poll_iunterval_ms=_KAFKA_MAX_INT_VALUE,
            **self._kwargs
        )
        consumer.subscribe([self._topic])

        while not self._stop_event.is_set():
            for message in consumer:
                try:
                    logger.info(f"Consuming {message.topic}-{message.partition}-{message.offset}")
                    self._callback_function(message)
                except Exception as exception:
                    logger.exception(f"The kafka event could not be consumed {exception}")
                if self._stop_event.is_set():
                    break

        logger.info(f"Stop event received for consumer of topic [{self._topic}]. Consumption will be stopped")
        consumer.close()
