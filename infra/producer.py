from abc import ABCMeta, abstractmethod
from kafka import KafkaProducer


class Producer:
    def __init__(self, kafka_producer_configuration, topic, **kwargs):
        print("Connecting to Bootstrap Server : ", kafka_producer_configuration.get_bootstrap_servers())
        self._kafka_producer = KafkaProducer(
            bootstrap_servers=kafka_producer_configuration.get_bootstrap_servers(),
            sasl_mechanism="PLAIN",
            security_protocol="SASL_SSL",
            sasl_plain_username=kafka_producer_configuration.get_sasl_plain_username(),
            sasl_plain_password=kafka_producer_configuration.get_sasl_plain_password(),
            api_version=(0, 10, 1),
            acks="all",
            **kwargs
        )
        self._topic = topic
        self._flush_timeout = kafka_producer_configuration.get_flush_timeout()

    def produce(self, message, **kwargs):
        self._kafka_producer.send(self._topic, message.encode("utf-8"), **kwargs)
        self._kafka_producer.flush(self._flush_timeout)


class KafkaProducerConfiguration(metaclass=ABCMeta):
    @abstractmethod
    def get_bootstrap_servers(self):
        pass

    @abstractmethod
    def get_flush_timeout(self):
        pass
