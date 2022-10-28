from infra.producer import Producer
from infra.domain.alert.alert import Alert

import logging
import json


class KafkaService:
    def __init__(self, producer: Producer):
        self.producer = producer

    def send(self, alert: Alert):
        message = alert.prepare_to_send()
        self.producer.produce(json.dumps(message))
