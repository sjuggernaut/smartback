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

    def test_GivenCommand_whenAssemble_thenReturnCalibrationAlert(self):
        alert = self.assembler.assemble(self.command_data)
        self.assertIsInstance(alert, Alert)
        self.assertIsInstance(alert, CalibrationAlert)

    def test_GivenCommandWithNoDevicesKey_whenAssemble_thenReturnCalibrationAlert(self):
        del self.command_data["devices"]
        alert = self.assembler.assemble(self.command_data)
        self.assertIsNot(alert, Alert)

    def test_GivenCommandWithNoStepKey_whenAssemble_thenReturnCalibrationAlert(self):
        del self.command_data["step"]
        alert = self.assembler.assemble(self.command_data)
        self.assertIsNot(alert, Alert)

    def test_GivenCommand_whenAssemble_thenReturnCalibrationAlertWithStepIDAndCommand(self):
        self.command_data["step"] = 10
        alert = self.assembler.assemble(self.command_data)
        self.assertEqual(alert.command, SensorCommands.set_calibration_start)
        self.assertEqual(alert.step, 10)

    def test_GivenCommand_whenAssemble_thenReturnAlertWithDevices(self):
        alert = self.assembler.assemble(self.command_data)
        self.assertDictEqual(alert.devices, {'semg': 1, 'ir': 2, 'inertial': 3})

