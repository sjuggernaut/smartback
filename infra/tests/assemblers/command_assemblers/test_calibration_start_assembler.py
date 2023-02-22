# Needed for tests
import django

django.setup()

from django.test import TestCase
from unittest.mock import patch, Mock

from infra.models import Session
from infra.domain.alert.alert import Alert
from infra.domain.alert.calibration_alert import CalibrationStartAlert
from infra.domain.sensor_commands import SensorCommands
from infra.assemblers.command_assemblers.calibration_start_assembler import CalibrationStartAssembler


class CalibrationStartAssemblerTest(TestCase):
    def setUp(self) -> None:
        self.assembler = CalibrationStartAssembler()
        self.command_data = {
            "user": "1",
            "command": "calibration_start",
            "type": "ipc_command",
            "devices": {
                "semg": "1",
                "inertial": "2",
                "ir": "3"
            }
        }

    @patch('infra.assemblers.command_assemblers.calibration_start_assembler.CalibrationStartAssembler._create_session')
    def test_GivenCommand_whenAssemble_thenReturnAlert(self, create_session):
        create_session.return_value = Mock(spec=Session)
        alert = self.assembler.assemble(self.command_data)
        self.assertIsInstance(alert, Alert)

    @patch('infra.assemblers.command_assemblers.calibration_start_assembler.CalibrationStartAssembler._create_session')
    def test_GivenCommand_thenReturnAlertWithCommandSetSession(self, create_session):
        create_session.return_value = Mock(spec=Session)
        alert = self.assembler.assemble(self.command_data)
        self.assertEqual(alert.command, SensorCommands.set_calibration_start)
        self.assertIsInstance(alert, CalibrationStartAlert)

    # @patch('infra.assemblers.command_assemblers.calibration_start_assembler.get_user_model')
    #     get_user_model.return_value.objects.get.return_value = user
