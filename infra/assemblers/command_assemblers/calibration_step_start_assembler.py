import logging

from infra.assemblers.kafka_assembler import KafkaAssembler
from infra.domain.alert.calibration_alert import CalibrationStepStartAlert
from infra.domain.sensor_commands import SensorCommands
from infra.models import *

from infra.domain.alert.alert import Alert

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
    def assemble(self, command_data: dict) -> Alert:
        logger.info(f"Received Calibration Step Start command from the User Interface.")

        if not all(keys in command_data for keys in ("user", "step")):
            logger.info("Calibration Start: User/step data not found in the message received from the user interface.")
            return False

        """
        ProcedureStep - selected by the user on the user interface 
        CalibrationStep - ID is to be sent to the Sensors.        
        """
        procedure_step_id = command_data.get("step")
        procedure_step = ProcedureStep.objects.get(id=procedure_step_id)
        user = command_data.get("user")
        calibration_step = self._create_calibration_step(procedure_step, user)

        alert = CalibrationStepStartAlert(command=SensorCommands.set_calibration_step_start.name,
                                          step=str(calibration_step.id))
        return alert

    def _create_calibration_step(self, procedure_step: ProcedureStep, user):
        active_session = Session.objects.filter(user=user).last()
        calibration_step = CalibrationStep(session=active_session, step=procedure_step)
        calibration_step.save()
        return calibration_step
