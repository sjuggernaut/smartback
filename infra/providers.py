import logging

from infra.domain.alert.kafka_alert import KafkaAlertApi
from infra.assemblers.semg_sensor_assembler import KafkaSEMGSensorAssembler
from infra.assemblers.ir_sensor_assembler import KafkaIRSensorAssembler
from infra.assemblers.inertial_sensor_assembler import KafkaInertialSensorAssembler
from infra.consumer import Consumer
from smartback.configuration import get_config
from infra.assemblers.error_handler import LoggingKafkaErrorHandler

logger = logging.getLogger(__name__)


def launch_providers(environment):
    """
    Starts the consumers for topics: IR Sensors, SEMG Sensors, Inertial Sensors Data.
    Each one of the topics has dedicated Kafka topics.
    :param environment:
    :return:
    """
    configuration = get_config(environment)
    # ir_sensor_consumer_thread = _create_ir_sensor_consumer_thread(configuration)
    semg_sensor_consumer_thread = _create_semg_sensor_consumer_thread(configuration)
    # inertial_sensor_consumer_thread = _create_inertial_sensor_consumer_thread(configuration)

    logger.info("Starting Consumer threads...")
    # ir_sensor_consumer_thread.start()
    semg_sensor_consumer_thread.start()
    # inertial_sensor_consumer_thread.start()


def _create_ir_sensor_consumer_thread(configuration):
    sensor_alert_api = KafkaAlertApi(
        KafkaIRSensorAssembler
    )
    return Consumer(
        configuration.get_kafka_consumer_configuration(),
        configuration.get_kafka_ir_sensor_topic(),
        LoggingKafkaErrorHandler(),
        callback_function=sensor_alert_api.accept_record
    )


def _create_semg_sensor_consumer_thread(configuration):
    sensor_alert_api = KafkaAlertApi(
        KafkaSEMGSensorAssembler
    )
    return Consumer(
        configuration.get_kafka_consumer_configuration(),
        configuration.get_kafka_semg_sensor_topic(),
        LoggingKafkaErrorHandler(),
        callback_function=sensor_alert_api.accept_record
    )


def _create_inertial_sensor_consumer_thread(configuration):
    sensor_alert_api = KafkaAlertApi(
        KafkaInertialSensorAssembler
    )
    return Consumer(
        configuration.get_kafka_consumer_configuration(),
        configuration.get_kafka_inertial_sensor_topic(),
        LoggingKafkaErrorHandler(),
        callback_function=sensor_alert_api.accept_record
    )
