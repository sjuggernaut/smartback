from abc import ABC, abstractmethod
from kafka.consumer.fetcher import ConsumerRecord
from infra.domain.alert.alert import Alert


class KafkaAssembler(ABC):
    @abstractmethod
    def assemble(self, kafka_message: ConsumerRecord) -> Alert:
        pass
