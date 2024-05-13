# Needed for tests
import django

django.setup()

from django.test import TestCase
from unittest.mock import Mock

from infra.assemblers.command_assemblers.calibration_step_start_assembler import CalibrationStepStartAssembler
from infra.domain.alert.calibration_alert import CalibrationAlert
from infra.domain.alert.alert import Alert
from infra.domain.sensor_commands import SensorCommands


class CalibrationStepStartAssemblerTest(TestCase):
    def setUp(self) -> None:
        self.assembler = CalibrationStepStartAssembler()
        self.command_data = {
            "user": "1",
            "step": "1",
            "command": "calibration_step_start",
            "type": "ipc_command",
            "devices": {
                "semg": 1,
                "ir": 2,
                "inertial": 3
            }
        }



