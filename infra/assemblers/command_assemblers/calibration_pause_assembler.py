import logging

from infra.assemblers.kafka_assembler import KafkaAssembler
from infra.domain.alert.alert import Alert
from infra.domain.alert.calibration_alert import CalibrationEndAlert
from infra.exceptions.filter_out import FilterOutException
from infra.models import *
from infra.domain.sensor_commands import SensorCommands
from infra.assemblers.command_assemblers.calibration.calibration_end_data_processor import CalibrationEndDataProcessor

logger = logging.getLogger(__name__)

"""
Command Name: Calibration_pause
Command Received From: User Interface  
Command Purpose: Calibration phase is pause when the user moves between possible steps in a procedure during calibration 
                 The User Interface application will send the command to Kafka topic: IPC                    
"""


class CalibrationPauseAssembler(KafkaAssembler):
    def assemble(self, command_data: dict) -> Alert:
        """
        :param command_data:
        :return:
        """
        logger.info(f"Received Calibration End command.")

        try:
            session_id = command_data.get("session")
            session = Session.objects.get(id=session_id)

            # Send calibration_pause command to user's sensors to pause the data sending process
            return CalibrationEndAlert(command=SensorCommands.set_calibration_pause.name, session=session_id)
        except Exception as e:
            raise FilterOutException(__name__, e)
