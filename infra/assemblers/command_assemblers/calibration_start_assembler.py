import logging

from infra.assemblers.kafka_assembler import KafkaAssembler
from infra.domain.command_process import CommandProcess

logger = logging.getLogger(__name__)


class CalibrationStepStartAssembler(KafkaAssembler):
    def assemble(self, command_data: dict) -> CommandProcess:
        logger.info(f"Received Calibration Phase Start command.")
