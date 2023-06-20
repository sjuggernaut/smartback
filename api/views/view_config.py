import os

from infra.assemblers.command_assemblers.command_assembler import CalibrationCommandAssembler
from smartback.configuration import get_config
from infra.producer import Producer
from infra.models import SessionTypes
from infra.service.kafka_service import KafkaService

environment = os.getenv("ENVIRONMENT")
configuration = get_config(environment)

command_assembler = CalibrationCommandAssembler()

session_types = {
    "treatment": SessionTypes.TREATMENT,
    "calibration": SessionTypes.CALIBRATION
}

environment = os.getenv('ENVIRONMENT')
configuration = get_config(environment)
producer = Producer(configuration.get_kafka_producer_configuration(), configuration.get_kafka_ipc_engine_topic())
kafka_service = KafkaService(producer)
