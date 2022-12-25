import logging

from infra.assemblers.kafka_assembler import KafkaAssembler
from infra.domain.alert.calibration_alert import CalibrationAlert
from infra.domain.sensor_commands import SensorCommands

logger = logging.getLogger(__name__)

"""
Command Name: Calibration_Step_Start
Command Received From: User Interface  
Command Purpose: A calibration Procedure Step is started by the user interface. This command is now sent to the sensors. 
                 Once the sensors receive the command: Commands.set_calibration_start, Sensors will start sending the data for each step.   
                 Each step selected by the user in the User interface will be processed here and sent to the Sensors. 
                 Sensor will send the Step ID and session ID along with the sensor specific data.
"""


class CalibrationStepStartAssembler(KafkaAssembler):
    def assemble(self, command_data: dict) -> CalibrationAlert:
        logger.info(f"Received Calibration Step Start command from the User Interface.")

        if not all(keys in command_data for keys in ("user", "devices", "step")):
            logger.info(
                "Calibration Start: User/devices/step data not found in the message received from the user interface.")
            return False

        # Step - selected by the user on the user interface, Step ID is to be sent to the Sensors.
        step_id = command_data.get("step")
        alert = CalibrationAlert(command=SensorCommands.set_calibration_start,
                                 step=step_id,
                                 devices=command_data.get("devices"))
        return alert
