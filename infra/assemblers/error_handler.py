import logging

from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)


class KafkaErrorHandler(metaclass=ABCMeta):
    @abstractmethod
    def unexpected_error_on_message_consumption(self, exception):
        pass


class LoggingKafkaErrorHandler(KafkaErrorHandler):
    def unexpected_error_on_message_consumption(self, exception):
        logger.exception("NoopKafkaErrorHandler.unexpected_error_on_message_consumption")
